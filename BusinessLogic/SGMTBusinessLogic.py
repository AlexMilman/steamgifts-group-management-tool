import time

import pylru
import sys

from BusinessLogic.ScrapingUtils import SteamGiftsScrapingUtils, SGToolsScrapingUtils, SteamRepScrapingUtils, \
    SteamScrapingUtils, SGToolsConsts, SteamGiftsConsts, SteamRepConsts, SteamConsts, SteamDBScrapingUtils
from Data.GameData import GameData
from Data.Group import Group

# Internal business logic of different SGMT commands
# Copyright (C) 2017  Alex Milman
from Data.GroupUser import GroupUser
from Database import MySqlConnector

GROUP_LRU_CACHE_SIZE = 100
GAME_LRU_CACHE_SIZE = 1000

# LRU cache used to hold data of last LRU_CACHE_SIZE groups. In order to cache the data and not retrieve it every time.
# Going forward need to consider using an external (persistent) cache server
groups_cache = pylru.lrucache(GROUP_LRU_CACHE_SIZE)
games_cache = pylru.lrucache(GAME_LRU_CACHE_SIZE)


def missing_after_n_giveaway(group_webpage, n, steam_thread):
    group = load_group(group_webpage)
    if not group:
        return None
    group_giveaways = group.group_giveaways
    group_users = group.group_users
    after_n_giveaways = SteamScrapingUtils.verify_after_n_giveaways(steam_thread, group_giveaways, group_users.keys())
    wins = get_user_wins(group)
    discrepancies = findDiscrepancies(n, wins, after_n_giveaways)
    return discrepancies


def get_user_wins(group_data):
    user_wins=dict()
    for giveaway in group_data.group_giveaways.values():
        for entry in giveaway.entries.values():
            user_name = entry.user_name
            if entry.winner and user_name in group_data.group_users.keys():
                if user_name not in user_wins:
                    user_wins[user_name] = set()
                user_wins[user_name].add(giveaway.link)
    return user_wins


def findDiscrepancies(N, wins, after_n_giveaways):
    discrepancies = dict()
    for user, won in wins.iteritems():
        after_n_user_giveaways = 0
        if user in after_n_giveaways:
            after_n_user_giveaways = len(after_n_giveaways[user])
        if (after_n_user_giveaways + 1) * N <= len(won):
            discrepancies[user] = 'won ' + str(len(won)) + ' times, but did after-' + str(N) + ' GAs only ' + str(after_n_user_giveaways) + ' times'
    return discrepancies


def get_all_after_n_giveaways_per_user(group_webpage, n, steam_thread):
    group = load_group(group_webpage)
    if not group:
        return None
    after_n_giveaways = SteamScrapingUtils.verify_after_n_giveaways(steam_thread, group.group_giveaways, group.group_users.keys())
    return after_n_giveaways


def get_all_user_giveaways(group_webpage):
    group = load_group(group_webpage)
    if not group:
        return None
    giveaways_per_user=dict()
    for giveaway in group.group_giveaways.values():
        poster = giveaway.creator
        if poster in group.group_users.keys():
            if poster not in giveaways_per_user:
                giveaways_per_user[poster] = set()
            giveaways_per_user[poster].add(giveaway.link)

    return giveaways_per_user


def get_all_user_wins(group_webpage):
    group = load_group(group_webpage)
    if not group:
        return None
    wins = get_user_wins(group)
    return wins


def get_stemagifts_to_steam_user_translation(group_webpage):
    group = load_group(group_webpage)
    if not group:
        return None
    steam_id_to_user = SteamScrapingUtils.get_steam_id_to_user_dict(group.group_users.values())
    return steam_id_to_user


def get_all_giveaways_in_group(group_webpage):
    group = load_group(group_webpage, load_users_data=False)
    if not group:
        return None
    return group.group_giveaways.values()


def get_all_users_in_group(group_webpage):
    group = load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    return group.group_users.keys()


def check_monthly(group_webpage, year_month, min_days=0, min_value=0.0, min_num_of_reviews=0, min_score=0,
                  alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0):
    response = ''
    group = load_group(group_webpage, limit_by_time=True, start_time=year_month + '-01', end_time=year_month + '-31')
    if not group:
        return None
    users = group.group_users.keys()
    monthly_posters = set()
    monthly_unfinished = dict()
    month = int(year_month.split('-')[1])
    for group_giveaway in group.group_giveaways.values():
        end_month = group_giveaway.end_time.tm_mon
        start_month = group_giveaway.start_time.tm_mon
        # If GA started in previous month, mark it as started on the 1th of the month
        if start_month == month - 1 and end_month == month:
            start_day = 1
            start_month = month
        else:
            start_day = group_giveaway.start_time.tm_mday
        end_day = group_giveaway.end_time.tm_mday
        if group_giveaway.creator in users and len(group_giveaway.groups) == 1\
                and start_month == month and end_month == month\
                and end_day - start_day >= min_days:
            game_name = group_giveaway.game_name
            game_data = load_game(game_name)
            check_game_data(game_data, game_name)
            if game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score):
                if group_giveaway.has_winners():
                    monthly_posters.add(group_giveaway.creator)
                else:
                    if group_giveaway.creator not in monthly_unfinished:
                        monthly_unfinished[group_giveaway.creator] = set()
                    monthly_unfinished[group_giveaway.creator].add(group_giveaway.link)

    response += '\n\nUsers with unfinished monthly GAs:\n'
    for user,links in monthly_unfinished.iteritems():
        response += 'User ' + SteamGiftsConsts.get_user_link(user) + ' giveaways: ' + parse_list(links) + '\n'

    response += '\n\nUsers without monthly giveaways:\n'
    for user in users:
        if user not in monthly_posters and user not in monthly_unfinished.keys():
            response += SteamGiftsConsts.get_user_link(user) + '\n'
    return response


def get_users_with_negative_steamgifts_ratio(group_webpage):
    group = load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    users_with_negative_sg_ratio = set()
    for group_user in group.group_users.values():
        if group_user.global_won > group_user.global_sent:
            users_with_negative_sg_ratio.add(group_user.user_name)
    return users_with_negative_sg_ratio


def get_users_with_negative_group_ratio(group_webpage):
    group = load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    users_with_negative_ratio=[]
    for user in group.group_users.values():
        if user.group_won > user.group_sent:
            users_with_negative_ratio.append(user.user_name)
    return users_with_negative_ratio


#TODO: Add giveaway entered time (from entries page)
def get_user_entered_giveaways(group_webpage, users, addition_date):
    group = load_group(group_webpage, load_users_data=False)
    if not group:
        return None
    response = ''
    users_list = users.split(',')
    for group_giveaway in group.group_giveaways.values():
        # Go over all giveaways not closed before "addition_date"
        if not addition_date or addition_date < time.strftime('%Y-%m-%d', group_giveaway.end_time):
            for user in users_list:
                if user in group_giveaway.entries:
                    response += 'User ' + user + ' entered giveaway: ' + group_giveaway.link + '\n'
    return response


def check_user_first_giveaway(group_webpage, users, addition_date=None, days_to_create_ga=0, min_ga_time=0,
                              min_value=0.0, min_num_of_reviews=0, min_score=0, alt_min_value=0.0,
                              alt_min_num_of_reviews=0, alt_min_score=0, check_entered_giveaways=False):
    group = load_group(group_webpage, load_users_data=False, limit_by_time=addition_date, start_time=addition_date)
    if not group:
        return None
    response = ''
    users_list = users.split(',')
    for group_giveaway in group.group_giveaways.values():
        game_name = group_giveaway.game_name
        if (  group_giveaway.creator in users_list
            and
                len(group_giveaway.groups) == 1
            and
                ((not addition_date or days_to_create_ga == 0)
                or (addition_date and days_to_create_ga > 0 and group_giveaway.start_time.tm_mday <= int(addition_date.split('-')[2]) + days_to_create_ga))
            and
                (min_ga_time == 0
                or (min_ga_time > 0 and group_giveaway.end_time.tm_mday - group_giveaway.start_time.tm_mday >= min_ga_time))):
            game_data = load_game(game_name)
            check_game_data(game_data, game_name)
            if game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value,alt_min_num_of_reviews, alt_min_score):
                response += 'User <A HREF="' + SteamGiftsConsts.get_user_link(group_giveaway.creator) + '">' + group_giveaway.creator + '</A> ' \
                            'first giveaway: <A HREF="' + group_giveaway.link + '">' + game_name + '</A> ' \
                          ' (Steam Value: ' + str(game_data.value) + ', Steam Score: ' + str(game_data.steam_score) + ', Num Of Reviews: ' + str(game_data.num_of_reviews) +')\n'

        # TODO: Add giveaway entered time (from entries page)
        # TODO: Fix this to check according to first user GA end time
        if check_entered_giveaways and (not addition_date or addition_date < time.strftime('%Y-%m-%d', group_giveaway.end_time)):
            for user in users_list:
                if user in group_giveaway.entries:
                    response += 'User <A HREF="' + SteamGiftsConsts.get_user_link(user) + '">' + user + '</A> ' \
                                'entered giveaway before his first giveaway was over: <A HREF="' + group_giveaway.link + '">' + game_name + '</A>\n'

    return response


def check_game_data(game_data, game_name):
    #TODO: Change to logger.error
    if not game_data:
        print 'Could not load game data: ' + game_name
    elif game_data.value == -1 or game_data.num_of_reviews == -1 or game_data.steam_score == -1:
        print 'Could not load full game data: ' + game_name


def game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score):
    if not game_data:
        return True
    if ((min_value == 0 or (game_data.value == 0 or game_data.value >= min_value))
         and (min_num_of_reviews == 0 or (game_data.num_of_reviews == 0 or min_num_of_reviews <= game_data.num_of_reviews))
         and (min_score == 0 or (game_data.steam_score == 0 or min_score <= game_data.steam_score))):
        return True
    if ((alt_min_value == 0 or (game_data.value == 0 or game_data.value >= alt_min_value))
         and (alt_min_num_of_reviews == 0 or (game_data.num_of_reviews == 0 or alt_min_num_of_reviews <= game_data.num_of_reviews))
         and (alt_min_score == 0 or (game_data.steam_score == 0 or alt_min_score <= game_data.steam_score))):
        return True
    return False


def user_check_rules(user_name, check_nonactivated=False, check_multiple_wins=False, check_real_cv_ratio=False, check_steamgifts_ratio=False, check_level=False, min_level=0, check_steamrep=False):
    broken_rules = dict()
    group_user=None
    if check_nonactivated and SGToolsScrapingUtils.check_nonactivated(user_name):
        append_map_list(broken_rules, user_name, 'Has non-activated games: ' + SGToolsConsts.SGTOOLS_CHECK_NONACTIVATED_LINK + user_name)

    if check_multiple_wins and SGToolsScrapingUtils.check_multiple_wins(user_name):
        append_map_list(broken_rules, user_name, 'Has multiple wins: ' + SGToolsConsts.SGTOOLS_CHECK_MULTIPLE_WINS_LINK + user_name)

    if check_real_cv_ratio and SGToolsScrapingUtils.check_real_cv_RATIO(user_name):
        append_map_list(broken_rules, user_name, 'Won more than Sent (Real CV value).\n'
                                                + 'Real CV Won: ' + SGToolsConsts.SGTOOLS_CHECK_WON_LINK + user_name + '\n'
                                                + 'Real CV Sent: ' + SGToolsConsts.SGTOOLS_CHECK_SENT_LINK + user_name)

    if check_steamgifts_ratio:
        group_user = load_user(group_user, user_name)
        if group_user.global_won > group_user.global_sent:
            append_map_list(broken_rules, user_name, 'Won more than Sent.\n'
                            + 'Won: ' + str(group_user.global_won) + '\n'
                            + 'Sent: ' + str(group_user.global_sent))

    if check_level and min_level > 0:
        group_user = load_user(group_user, user_name)
        if group_user.level < float(min_level):
            append_map_list(broken_rules, user_name, 'User level is less than ' + str(min_level))

    if check_steamrep:
        user_steam_id = SteamGiftsScrapingUtils.get_user_steam_id(user_name)
        if user_steam_id and not SteamRepScrapingUtils.check_user_not_public_or_banned(user_steam_id):
            append_map_list(broken_rules, user_name, 'User is not public or banned: ' + SteamRepConsts.get_steamrep_link(user_steam_id))

    return broken_rules


def load_user(group_user, user_name):
    if not group_user:
        group_user = MySqlConnector.get_user_data(user_name)
    if not group_user:
        group_user = GroupUser(user_name)
        SteamGiftsScrapingUtils.update_user_additional_data(group_user)
        MySqlConnector.save_user(group_user)
    return group_user


def test(group_webpage):
    # group = add_new_group(group_webpage, '')
    # MySqlConnector.save_group(group_webpage, group)
    # group = MySqlConnector.load_group(group_webpage)

    # for group_user in group.group_users.values():
    #     print '\nUser: ' + group_user.user_name
    #     for message in user_check_rules(group_user.user_name, check_real_cv_value=True):
    #         print message
    #     if group_user.global_won > group_user.global_sent:
    #         print 'User ' + group_user.user_name + ' has negative global gifts ratio'
    game = GameData('Chroma Squad', 'http://store.steampowered.com/app/251130/', 15)

    try:
        SteamScrapingUtils.update_game_additional_data(game)
    except:
        SteamDBScrapingUtils.update_game_additional_data(game)

def load_group(group_webpage, load_users_data=True, load_giveaway_data=True, limit_by_time=False, start_time=None, end_time=None):
    if group_webpage in groups_cache:
        group = groups_cache[group_webpage]
    else:
        group = MySqlConnector.load_group(group_webpage, load_users_data, load_giveaway_data, limit_by_time, start_time, end_time)
        groups_cache[group_webpage] = group
    return group


def add_new_group(group_webpage, cookies):
    update_group_data(group_webpage, cookies, Group())


def update_existing_group(group_webpage, cookies):
    group = load_group(group_webpage)
    if not group:
        return None
    update_group_data(group_webpage, cookies, group)


def update_group_data(group_webpage, cookies, group):
    group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage)
    existing_users = MySqlConnector.check_existing_users(group_users.keys())
    for group_user in group_users.values():
        if group_user.user_name not in existing_users:
            SteamGiftsScrapingUtils.update_user_additional_data(group_user)

    group_giveaways, games = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies, group.group_giveaways)
    MySqlConnector.save_group(group_webpage, Group(group_users, group_giveaways), existing_users, group)

    existing_games = MySqlConnector.check_existing_games(games.keys())
    for game in games.values():
        if game.game_name not in existing_games and game.game_link.startswith(SteamConsts.STEAM_GAME_LINK):
            # TODO: Add fallback from SteamDB
            try:
                SteamScrapingUtils.update_game_additional_data(game)
            except:
                print 'Cannot add additional data for ' + game.game_name + ' ERROR: %s', sys.exc_info()[0]
    MySqlConnector.save_games(games, existing_games)


#TODO: Implement with scheduler
def update_all_groups(cookies):
    #Load list of all groups from DB
    #For each group, run: update_group_data
    pass


def update_users_data():
    #Go over all DB users, and update their data
    pass


def update_games_data():
    #Go over all DB games, and update their data
    pass


def load_game(game_name):
    game_data=None
    if game_name in games_cache:
        game_data = games_cache[game_name]
    if not game_data:
        game_data = MySqlConnector.get_game_data(game_name)
        games_cache[game_name] = game_data
    return game_data


def parse_list(list, prefix=''):
    result = ''
    for item in list:
        result += prefix + item + ', '

    return result[:-2]


def append_map_list(map_list, user, message):
    if user not in map_list:
        map_list[user] = []
    map_list[user].append(message)
