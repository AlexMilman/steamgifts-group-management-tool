import ConfigParser
import datetime
import traceback

from dateutil.relativedelta import relativedelta

from BusinessLogic.ScrapingUtils import SteamGiftsScrapingUtils, SGToolsScrapingUtils, SteamRepScrapingUtils, \
    SteamScrapingUtils, SteamGiftsConsts, SteamRepConsts, SteamConsts, SteamDBScrapingUtils, BarterVGScrapingUtils
from BusinessLogic.Utils import LogUtils
from Data.GameData import GameData
from Data.Group import Group
from Data.GroupUser import GroupUser
from Database import MySqlConnector

# Internal business logic of different SGMT commands
# Copyright (C) 2017  Alex Milman

config = ConfigParser.ConfigParser()
config.read('application.config')
common_cookies = config.get('Web', 'Cookies')


def check_monthly(group_webpage, year_month, min_days=0, min_entries=1, min_value=0.0, min_num_of_reviews=0, min_score=0,
                  alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0,
                  alt2_min_value=0.0, alt2_min_num_of_reviews=0, alt2_min_score=0,
                  min_entries_override=0, ignore_inactive_users=False, ignore_cakeday_users=False):
    group = get_group_by_year_month(group_webpage, year_month)
    if not group:
        return None
    month = int(year_month.split('-')[1])
    users = group.group_users
    monthly_posters = set()
    monthly_active = set()
    monthly_inactive = None
    monthly_unfinished = dict()
    cakeday_users = None
    for group_giveaway in group.group_giveaways.values():
        if ignore_inactive_users:
            monthly_active.update([x.user_name for x in group_giveaway.entries.values() if x.entry_time.month == month])
        end_month = group_giveaway.end_time.month
        start_month = group_giveaway.start_time.month
        # If GA started in previous month, mark it as started on the 1th of the month
        if (start_month == month - 1 or (start_month == 12 and month == 1)) and end_month == month :
            start_day = 1
            start_month = month
        else:
            start_day = group_giveaway.start_time.day
        end_day = group_giveaway.end_time.day
        creator = group_giveaway.creator
        if creator in users and len(group_giveaway.groups) == 1\
                and start_month == month and end_month == month\
                and end_day - start_day + 1 >= min_days:
            game_name = group_giveaway.game_name
            game_data = MySqlConnector.get_game_data(game_name)
            check_game_data(game_data, game_name)
            if len(group_giveaway.entries) > min_entries_override > 0:
                monthly_posters.add(creator)
            if game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score, alt2_min_value, alt2_min_num_of_reviews, alt2_min_score):
                if group_giveaway.has_winners() and len(group_giveaway.entries) > min_entries:
                    monthly_posters.add(creator)
                elif group_giveaway.end_time > datetime.datetime.now() or len(group_giveaway.entries) > 0:
                    if creator not in monthly_unfinished:
                        monthly_unfinished[creator] = set()
                    monthly_unfinished[creator].add(group_giveaway)

    if ignore_inactive_users:
        monthly_inactive = [x for x in users.keys() if x not in monthly_active]

    if ignore_cakeday_users:
        cakeday_users = [user for user,data in users.iteritems() if data.creation_time and data.creation_time.month == month]

    return users, monthly_posters, monthly_unfinished, monthly_inactive, cakeday_users


def check_giveaways_valid(group_webpage, start_date=None, min_days=0, min_entries=1,
                          min_value=0.0, min_num_of_reviews=0, min_score=0,
                          alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0,
                          alt2_min_value=0.0, alt2_min_num_of_reviews=0, alt2_min_score=0, free_group_only=False):
    group = MySqlConnector.load_group(group_webpage, limit_by_time=start_date, starts_after_str=start_date)
    if not group:
        return None
    free_games_list = []
    invalid_giveaways = dict()
    free_games = dict()
    games_to_load = []
    users = group.group_users.keys()

    if free_group_only:
        free_games_list = MySqlConnector.get_free_games()

    for group_giveaway in group.group_giveaways.values():
        if group_giveaway.creator in users:
            games_to_load.append(group_giveaway.game_name)
    games = MySqlConnector.get_existing_games_data(games_to_load)

    for group_giveaway in group.group_giveaways.values():
        creator = group_giveaway.creator
        if creator in users:
            game_name = group_giveaway.game_name
            if game_name not in games:
                LogUtils.log_warning('Game ' + str(game_name) + ' was not found in loaded games')
                if game_name.decode('utf-8') in games:
                    LogUtils.log_warning('Using ' + game_name.decode('utf-8') + ' instead')
                    games[game_name] = games[game_name.decode('utf-8')]
                else:
                    games[game_name] = MySqlConnector.get_game_data(game_name)
            game_data = games[game_name]
            check_game_data(game_data, game_name)
            if not game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score, alt2_min_value, alt2_min_num_of_reviews, alt2_min_score)\
                    or (group_giveaway.end_time - group_giveaway.start_time).days < min_days\
                    or (datetime.datetime.now() > group_giveaway.end_time and len(group_giveaway.entries) < min_entries):
                if creator not in invalid_giveaways:
                    invalid_giveaways[creator] = set()
                invalid_giveaways[creator].add(group_giveaway)
            if free_group_only and group_giveaway.game_name in free_games_list and len(group_giveaway.groups) > 1:
                if creator not in free_games:
                    free_games[creator] = set()
                free_games[creator].add(group_giveaway)

    return invalid_giveaways, free_games, games


def get_user_all_giveways(group_webpage, user, start_time):
    group = MySqlConnector.load_group(group_webpage, load_users_data=False, limit_by_time=start_time, starts_after_str=start_time)
    if not group:
        return None
    created_giveaways=[]
    entered_giveaways=[]
    games=dict()
    for group_giveaway in group.group_giveaways.values():
        if not start_time or start_time <= group_giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S'):
            game_name = group_giveaway.game_name
            if group_giveaway.creator == user:
                created_giveaways.append(group_giveaway)
                games[game_name] = MySqlConnector.get_game_data(game_name)
            elif user in group_giveaway.entries.keys():
                entered_giveaways.append(group_giveaway)
                games[game_name] = MySqlConnector.get_game_data(game_name)

    return created_giveaways, entered_giveaways, games


def get_group_summary(group_webpage, start_time):
    group = MySqlConnector.load_group(group_webpage, limit_by_time=start_time, starts_after_str=start_time)
    if not group:
        return None
    all_group_users = group.group_users.keys()
    users_created = dict()
    users_entered = dict()
    users_won = dict()
    group_games_count=0
    group_games_value=0.0
    group_games_without_data=0
    group_games_total_score=0.0
    group_games_total_num_of_reviews=0.0
    group_total_entered=0.0
    group_total_won=0.0
    for group_giveaway in group.group_giveaways.values():
        creator = group_giveaway.creator
        # Go over all giveaways started after "addition_date"
        if not start_time or start_time <= group_giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S'):
            group_games_count += 1
            try:
                game_data = MySqlConnector.get_game_data(group_giveaway.game_name)
            except Exception as e:
                LogUtils.log_error(u'Crashed while trying to load game data of ' + group_giveaway.game_name.decode('utf-8') + u'. Reason: ' + str(e))
                traceback.print_exc()
                continue
            if not game_data:
                LogUtils.log_error(u'Could not load game data: ' + group_giveaway.game_name.decode('utf-8'))
            score = -1
            num_of_reviews = -1
            value = -1
            if game_data:
                value = game_data.value
                group_games_value += value
                score = game_data.steam_score
                num_of_reviews = game_data.num_of_reviews
            game_data_available = score != -1 and num_of_reviews != -1
            if game_data_available:
                group_games_total_score += score
                group_games_total_num_of_reviews += num_of_reviews
            else:
                group_games_without_data += 1

            # Number of created GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
            if creator in all_group_users:
                if creator not in users_created:
                    users_created[creator] = [0, 0, 0, 0, 0]
                users_created[creator][0] += 1
                if value != -1:
                    users_created[creator][1] += value
                if game_data_available:
                    users_created[creator][2] += 1
                    if score != -1:
                        users_created[creator][3] += score
                    if num_of_reviews != -1:
                        users_created[creator][4] += num_of_reviews

            giveaway_entries = group_giveaway.entries.values()
            num_of_giveaway_entries = len(giveaway_entries)
            for entry in giveaway_entries:
                user_name = entry.user_name
                if user_name not in all_group_users:
                    continue
                group_total_entered += 1
                # Number of entered GAs, Number of Unique GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
                if user_name not in users_entered:
                    users_entered[user_name] = [0, 0, 0, 0, 0, 0, 0]
                users_entered[user_name][0] += 1
                users_entered[user_name][1] += (1.0 / num_of_giveaway_entries)
                if len(group_giveaway.groups) == 1:
                    users_entered[user_name][2] += 1
                if value != -1:
                    users_entered[user_name][3] += value
                if game_data_available:
                    users_entered[user_name][4] += 1
                    if score != -1:
                        users_entered[user_name][5] += score
                    if num_of_reviews != -1:
                        users_entered[user_name][6] += num_of_reviews

                if entry.winner:
                    group_total_won += 1
                    # Number of won GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
                    if user_name not in users_won:
                        users_won[user_name] = [0, 0, 0, 0, 0]
                    users_won[user_name][0] += 1
                    if value != -1:
                        users_won[user_name][1] += value
                    if game_data_available:
                        users_won[user_name][2] += 1
                        if score != -1:
                            users_won[user_name][3] += score
                        if num_of_reviews != -1:
                            users_won[user_name][4] += num_of_reviews


    group_average_game_value = group_games_value / group_games_count
    group_average_game_score = group_games_total_score / (group_games_count - group_games_without_data)
    group_average_game_num_of_reviews = group_games_total_num_of_reviews / (group_games_count - group_games_without_data)
    # Total Giveaways Count, Total Games Value, Average games value, Average Game Score, Average Game NumOfReviews, Average number of entered per game, Average number of created per user, Average number of entrered per user, Average number of won per user
    total_group_data = (group_games_count, group_games_value, group_average_game_value, group_average_game_score, group_average_game_num_of_reviews, group_total_entered / group_games_count, float(group_games_count) / len(all_group_users), group_total_entered / len(all_group_users), group_total_won / len(all_group_users))

    # Number of created GAs, Total Value, Average Value, Average Score, Average NumOfReviews
    # Number of entered GAs, Percentage of unique, Average Value, Average Score, Average Num Of Reviews
    # If avialable: number of won GAs, Winning percentage, Average Value, Average Score, Average Num Of Reviews
    users_data = dict()
    for user in users_created.keys():
        if user not in users_data:
            users_data[user] = [(),(),()]
        # Number of created GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
        user_data = users_created[user]
        # Number of created GAs, Total Value, Average Value, Average Score, Average NumOfReviews
        if user_data[2] > 0:
            users_data[user][0] = (user_data[0], user_data[1], float(user_data[1]) / user_data[0], float(user_data[3]) / user_data[2], float(user_data[4]) / user_data[2])
        else:
            users_data[user][0] = (user_data[0], user_data[1], float(user_data[1]) / user_data[0], 0, 0)

    for user in users_entered.keys():
        if user not in users_data:
            users_data[user] = [(),(),()]
        # Number of entered GAs, Total number of entries in GAs he entered, Number of Shared GAs, Total Value,
        # Number of GAs with data, Total Score, Total NumOfReviews
        user_data = users_entered[user]
        # Number of entered GAs, Probability of winning, Percentage of unique, Total Value, Average Value, Average Score, Average Num Of Reviews
        if user_data[3] > 0 and user_data[4] > 0:
            users_data[user][1] = (user_data[0], user_data[1] * 100, float(user_data[2]) / user_data[0] * 100, user_data[3], float(user_data[3]) / user_data[0], float(user_data[5]) / user_data[4], float(user_data[6]) / user_data[4])
        else:
            users_data[user][1] = (user_data[0], user_data[1] * 100, float(user_data[2]) / user_data[0] * 100, user_data[3], float(user_data[3]) / user_data[0], 0, 0)
        if user in users_won:
            # Number of won GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
            user_data = users_won[user]
            # Number of won GAs, Winning percentage, Total value, Average Value, Average Score, Average Num Of Reviews
            if user_data[2] > 0:
                users_data[user][2] = (user_data[0], float(user_data[0]) / users_data[user][1][0] * 100, user_data[1], float(user_data[1]) / user_data[0], float(user_data[3]) / user_data[2], float(user_data[4]) / user_data[2])
            else:
                users_data[user][2] = (user_data[0], float(user_data[0]) / users_data[user][1][0] * 100, user_data[1], float(user_data[1]) / user_data[0], 0, 0)

    return total_group_data, users_data


def check_user_first_giveaway(group_webpage, users, addition_date, days_to_create_ga=0, min_ga_time=0, min_entries=1,
                              min_value=0.0, min_num_of_reviews=0, min_score=0,
                              alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0,
                              alt2_min_game_value=0, alt2_min_steam_num_of_reviews=0, alt2_min_steam_score=0,
                              check_entered_giveaways=False):
    group = MySqlConnector.load_group(group_webpage, load_users_data=False, limit_by_time=True, ends_after_str=addition_date)
    if not group:
        return None
    users_list = users.split(',')
    user_added_time = datetime.datetime.strptime(addition_date, '%Y-%m-%d')
    user_end_time=dict()
    user_first_giveaway=dict()
    succesfully_ended=dict()
    user_no_giveaway=set()
    for group_giveaway in group.group_giveaways.values():
        game_name = group_giveaway.game_name
        user_name = group_giveaway.creator
        if (user_name in users_list
            and
                len(group_giveaway.groups) == 1
            and
                (days_to_create_ga == 0 or group_giveaway.start_time <= user_added_time + datetime.timedelta(days=days_to_create_ga + 1))
            and
                (min_ga_time == 0
                or (min_ga_time > 0 and group_giveaway.end_time - group_giveaway.start_time >= datetime.timedelta(days=min_ga_time - 1)))):
            game_data = MySqlConnector.get_game_data(game_name)
            check_game_data(game_data, game_name)
            if game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score, alt2_min_game_value, alt2_min_steam_num_of_reviews, alt2_min_steam_score):
                if user_name not in user_end_time or group_giveaway.end_time < user_end_time[user_name]:
                    user_end_time[user_name] = group_giveaway.end_time
                if user_name not in user_first_giveaway:
                    user_first_giveaway[user_name] = set()
                user_first_giveaway[user_name].add((group_giveaway, game_data))

                if datetime.datetime.now() > group_giveaway.end_time and group_giveaway.has_winners() and len(group_giveaway.entries) > min_entries:
                    if user_name not in succesfully_ended:
                        succesfully_ended[user_name] = set()
                    succesfully_ended[user_name].add(group_giveaway.link)

    for user in users_list:
        if user not in user_end_time.keys():
            user_no_giveaway.add(user)

    partial_group_webpage = group_webpage.split(SteamGiftsConsts.STEAMGIFTS_LINK)[1]
    user_entered_giveaway=dict()
    for group_giveaway in group.group_giveaways.values():
        if check_entered_giveaways and user_added_time < group_giveaway.end_time:
            for user in users_list:
                if user in group_giveaway.entries \
                        and group_giveaway.entries[user].entry_time >= user_added_time \
                        and (user not in user_end_time or group_giveaway.entries[user].entry_time < user_end_time[user])\
                        and (len(group_giveaway.groups) == 1 or not SteamGiftsScrapingUtils.is_user_in_group(user, filter(lambda x: x != partial_group_webpage, group_giveaway.groups))):
                    #TODO: Add "Whitelist detected" warning
                    if user not in user_entered_giveaway:
                        user_entered_giveaway[user] = set()
                    user_entered_giveaway[user].add(group_giveaway)

    time_to_create_over = False
    if days_to_create_ga > 0 and datetime.date.today() > user_added_time.date() + datetime.timedelta(days=days_to_create_ga + 1):
        time_to_create_over = True

    return user_first_giveaway, succesfully_ended, user_no_giveaway, user_entered_giveaway, time_to_create_over


def check_game_data(game_data, game_name):
    if not game_data:
        LogUtils.log_error(u'Could not load game data: ' + game_name.decode('utf-8'))
    elif game_data.value == -1 or game_data.num_of_reviews == -1 or game_data.steam_score == -1:
        LogUtils.log_error(u'Could not load full game data: ' + game_name.decode('utf-8'))


def game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0, alt2_min_value=0.0, alt2_min_num_of_reviews=0, alt2_min_score=0):
    if not game_data:
        return True
    if ((min_value == 0 or (game_data.value == 0 or game_data.value >= min_value))
         and (min_num_of_reviews == 0 or (game_data.num_of_reviews == -1 or min_num_of_reviews <= game_data.num_of_reviews))
         and (min_score == 0 or (game_data.steam_score == -1 or min_score <= game_data.steam_score))):
        return True
    if ((alt_min_value != 0 or alt_min_score != 0 or alt_min_num_of_reviews != 0)
        and (alt_min_value == 0 or (game_data.value == 0 or game_data.value >= alt_min_value))
        and (alt_min_num_of_reviews == 0 or (game_data.num_of_reviews == -1 or alt_min_num_of_reviews <= game_data.num_of_reviews))
        and (alt_min_score == 0 or (game_data.steam_score == -1 or alt_min_score <= game_data.steam_score))):
        return True
    if ((alt2_min_value != 0 or alt2_min_score != 0 or alt2_min_num_of_reviews != 0)
        and (alt2_min_value == 0 or (game_data.value == 0 or game_data.value >= alt2_min_value))
        and (alt2_min_num_of_reviews == 0 or (game_data.num_of_reviews == -1 or alt2_min_num_of_reviews <= game_data.num_of_reviews))
        and (alt2_min_score == 0 or (game_data.steam_score == -1 or alt2_min_score <= game_data.steam_score))):
        return True
    return False


def group_users_check_rules(group_webpage, check_nonactivated=False, check_multiple_wins=False, check_real_cv_ratio=False, check_steamgifts_ratio=False, check_level=False, min_level=0, check_steamrep=False):
    group = MySqlConnector.load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    result=dict()
    for user_name in group.group_users.keys():
        nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, level, steamrep = user_check_rules(user_name, check_nonactivated, check_multiple_wins, check_real_cv_ratio, check_steamgifts_ratio, check_level, min_level, check_steamrep)
        result[user_name] = (nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, level, steamrep)
    return result


def user_check_rules(user_name, check_nonactivated=False, check_multiple_wins=False, check_real_cv_ratio=False, check_steamgifts_ratio=False, check_level=False, min_level=0, check_steamrep=False):
    nonactivated=False
    multiple_wins=False
    real_cv_ratio=False
    steamgifts_ratio=None
    level=None
    steamrep=None

    if check_nonactivated:
        LogUtils.log_info('Checking user ' + user_name + ' for non-activated games')
        if SGToolsScrapingUtils.check_nonactivated(user_name):
            nonactivated=True

    if check_multiple_wins:
        LogUtils.log_info('Checking user ' + user_name + ' for multiple wins')
        if SGToolsScrapingUtils.check_multiple_wins(user_name):
            multiple_wins=True

    if check_real_cv_ratio:
        LogUtils.log_info('Checking user ' + user_name + ' for Real CV ratio')
        if SGToolsScrapingUtils.check_real_cv_RATIO(user_name):
            real_cv_ratio=True

    if check_steamgifts_ratio or (check_level and min_level > 0):
        global_won, global_sent, user_level = SteamGiftsScrapingUtils.get_user_contribution_data(user_name)
        if check_steamgifts_ratio:
            LogUtils.log_info('Checking user ' + user_name + ' for SteamGifts Global ratio')
            if global_won > global_sent:
                steamgifts_ratio = (global_won, global_sent)
        if check_level and min_level > 0:
            LogUtils.log_info('Checking user ' + user_name + ' for minimal level')
            if user_level < float(min_level):
                level = min_level

    if check_steamrep:
        LogUtils.log_info('Checking user ' + user_name + ' in SteamRep')
        user_steam_id = SteamGiftsScrapingUtils.get_user_steam_id(user_name)
        if user_steam_id and not SteamRepScrapingUtils.check_user_not_public_or_banned(user_steam_id):
            steamrep=SteamRepConsts.get_steamrep_link(user_steam_id)

    return nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, level, steamrep


def load_user(group_user, user_name):
    if not group_user:
        group_user = GroupUser(user_name)
        SteamGiftsScrapingUtils.update_user_additional_data(group_user)
        SteamScrapingUtils.update_user_additional_data(group_user)
    return group_user


def test():
    # from BusinessLogic.Utils import WebUtils
    # group = MySqlConnector.load_group('https://www.steamgifts.com/group/6HSPr/qgg-group')
    # print WebUtils.get_page_content('https://www.steamgifts.com/giveaway/JtzUN/broken-sword-5-the-serpents-curse', cookies=group.cookies)
    # group = add_new_group(group_webpage, '')
    # MySqlConnector.save_group(group_webpage, group)
    # group = MySqlConnector.load_group(group_webpage)
    # SteamScrapingUtils.get_steam_user_name_from_steam_id('76561198018110309')

    # for group_user in group.group_users.values():
    #     print '\nUser: ' + group_user.user_name
    #     for message in user_check_rules(group_user.user_name, check_real_cv_value=True):
    #         print message
    #     if group_user.global_won > group_user.global_sent:
    #         print 'User ' + group_user.user_name + ' has negative global gifts ratio'
    # game = GameData('Conarium', 'https://store.steampowered.com/app/313780/Conarium/', 20)
    # update_game_data(game)
    # MySqlConnector.update_existing_games([game])
    #
    # MySqlConnector.get_game_data('Conarium')
    # try:
    #     SteamScrapingUtils.get_game_additional_data(game.game_name, game.game_link)
    # except:
    # user = GroupUser('a404381120')
    # SteamGiftsScrapingUtils.update_user_additional_data(user)
    # MySqlConnector.update_existing_users([user])
    # MySqlConnector.get_users_by_names(['a404381120'])
    # pass
    # free_games = BarterVGScrapingUtils.get_free_games_list()
    SteamGiftsScrapingUtils.get_group_giveaways("https://www.steamgifts.com/group/h1441/qgg-companion-group", "_ga=GA1.2.2030495629.1584053874; __qca=P0-1161601042-1638994062738; _gid=GA1.2.330070482.1655743244; __gads=ID=b71d92a741f24267:T=1655743245:S=ALNI_MYfi4hLpBw_rgssD43S41LALYTBSQ; __gpi=UID=00000355be47fc49:T=1648924086:RT=1655743245:S=ALNI_MaJfOgTTvEPmzIvkrkNA8QDs7yj4A; PHPSESSID=0ho3kl39mvj11k967u5r87v4v40map7hmg20gab3ctf34puu; _gat_gtag_UA_3791796_9=1", dict())
    pass


def lazy_add_group(group_webpage, cookies):
    if not cookies:
        cookies = ''
    group_name = SteamGiftsScrapingUtils.get_group_name(group_webpage, cookies)
    MySqlConnector.save_empty_group(group_name, group_webpage, cookies)
    return group_name


def add_new_group(group_webpage, cookies, start_date=None):
    group_name = SteamGiftsScrapingUtils.get_group_name(group_webpage)
    if not cookies:
        cookies = common_cookies
    games = update_group_data(group_webpage, cookies, Group(group_name=group_name, group_webpage=group_webpage, cookies=cookies), force_full_run=True, start_date=start_date)
    update_games_data(games)


def update_existing_group(group_webpage, start_date=None, end_date=None, force_full_run=False, update_games=False):
    group = MySqlConnector.load_group(group_webpage, fetch_not_started_giveaways=True)
    if not group:
        return None
    cookies = common_cookies
    if group.cookies:
        cookies = group.cookies
    games = update_group_data(group_webpage, cookies, group, start_date=start_date, end_date=end_date, force_full_run=force_full_run)
    if update_games:
        update_games_data(games, update_value=True)


def get_groups():
    groups = MySqlConnector.get_all_groups()
    empty_groups = MySqlConnector.get_all_empty_groups()
    return groups, empty_groups


def get_groups_with_users():
    return MySqlConnector.get_all_groups_with_users()


def update_games_data(games, update_value=False):
    games_to_add = []
    games_to_update_value = []
    existing_games = MySqlConnector.get_existing_games_data(games.keys())
    for game in sorted(games.values(), key=lambda x: x.game_name):
        game_name = game.game_name.decode('utf-8')
        if game_name not in existing_games.keys():
            update_game_data(game)
            games_to_add.append(game)
        elif update_value and game.value != existing_games[game_name].value:
            games_to_update_value.append(game)

    if games_to_add:
        MySqlConnector.save_games(games_to_add)

    if games_to_update_value:
        MySqlConnector.update_existing_games(games_to_update_value)


def update_game_data(game):
    if game.game_link.startswith('http:'):
        # Converting all HTTP links into HTTPS
        game.game_link = game.game_link.replace('http', 'https')
    game_link = game.game_link
    game_name = game.game_name
    try:
        steam_score = 0
        num_of_reviews = 0
        if game_link.startswith(SteamConsts.STEAM_GAME_LINK):
            try:
                steam_score, num_of_reviews = SteamScrapingUtils.get_game_additional_data(game_name, game_link)
            except Exception as e:
                LogUtils.log_error('Error extracting Steam data for game: ' + game_name + ' at link: ' + game_link)
                LogUtils.log_error("Exception: " + str(e))
                try:
                    steam_score, num_of_reviews = SteamDBScrapingUtils.get_game_additional_data(game_name, game_link)
                except Exception as e:
                    LogUtils.log_error('Error extracting SteamDB data for game: ' + game_name + ' at link: ' + game_link)
                    LogUtils.log_error("Exception: " + str(e))
            game.steam_score = steam_score
            game.num_of_reviews = num_of_reviews
            if (not steam_score and not num_of_reviews) or (steam_score == 0 and num_of_reviews == 0):
                LogUtils.log_error('Unable to extract Steam Score & Number of reviews for: ' + game_name)
        elif game_link.startswith(SteamConsts.STEAM_PACKAGE_LINK):
            chosen_score = -1
            chosen_num_of_reviews = -1
            package_games = SteamScrapingUtils.get_games_from_package(game_name, game_link)
            i = 0
            for package_url in package_games:
                tmp_game_name = game_name + ' - package #' + str(i)
                try:
                    steam_score, num_of_reviews = SteamScrapingUtils.get_game_additional_data(tmp_game_name, package_url)
                except:
                    try:
                        steam_score, num_of_reviews = SteamDBScrapingUtils.get_game_additional_data(tmp_game_name, package_url)
                    except:
                        LogUtils.log_warning('Unable to extract Steam Score & Number of reviews for package: ' + package_url)
                if num_of_reviews > chosen_num_of_reviews:
                    chosen_score = steam_score
                    chosen_num_of_reviews = num_of_reviews
                i += 1
            game.steam_score = chosen_score
            game.num_of_reviews = chosen_num_of_reviews
        else:
            LogUtils.log_error('Don\'t know how to handle game: ' + game_name + ' at ' + game_link)
    except Exception as e:
        LogUtils.log_error('Cannot add additional data for game: ' + game_name + ' ERROR: ' + str(e))
        traceback.print_exc()


def update_group_data(group_webpage, cookies, group, force_full_run=False, start_date=None, end_date=None):
    group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage)
    if not group_users:
        LogUtils.log_error("group_users is empty")
        return dict()
    existing_users = MySqlConnector.check_existing_users(group_users.keys())
    for group_user in group_users.values():
        if group_user.user_name not in existing_users:
            try:
                SteamGiftsScrapingUtils.update_user_additional_data(group_user)
                SteamScrapingUtils.update_user_additional_data(group_user)
            except Exception as e:
                LogUtils.log_error('Cannot add additional data for user: ' + group_user.user_name + ' ERROR: ' + str(e))
                traceback.print_exc()

    group_giveaways, ignored_giveaways, games, reached_threshold = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies, group.group_giveaways, force_full_run=force_full_run, start_date=start_date, end_date=end_date)
    if not reached_threshold:
        remove_deleted_giveaways(cookies, group, group_giveaways, ignored_giveaways)
    MySqlConnector.save_group(group_webpage, Group(group_users, group_giveaways, group_webpage=group_webpage, cookies=cookies, group_name=group.group_name), existing_users, group)

    return games


def remove_deleted_giveaways(cookies, group, updated_group_giveaways, ignored_group_giveaways):
    # If any existing GA is missing from newly parsed data - remove it from group giveaways.
    giveaways_sorted_by_end_time = sorted(filter(lambda x: x.end_time, updated_group_giveaways.values()), key=lambda x: x.end_time)
    if not giveaways_sorted_by_end_time:
        return
    earliest_giveaway_end_time = giveaways_sorted_by_end_time[0].end_time
    for giveaway in sorted(filter(lambda x: x.end_time, group.group_giveaways.values()), key=lambda x: x.end_time, reverse=True):
        if giveaway.end_time < earliest_giveaway_end_time:
            break
        if giveaway.link not in updated_group_giveaways and giveaway.link not in ignored_group_giveaways and not giveaway.has_winners() and SteamGiftsScrapingUtils.is_giveaway_deleted(giveaway.link, cookies):
            LogUtils.log_info('Removing deleted giveaway: ' + giveaway.link)
            group.group_giveaways.pop(giveaway.link, None)


def update_all_db_groups():
    #Load list of all groups from DB
    groups, empty_groups = get_groups()
    LogUtils.log_info("Updating groups: " + str(groups.keys()))
    #For each existing group, run: update_group_data from last 2 months
    start_date = (datetime.datetime.now() - relativedelta(months=1)).replace(day=1).strftime('%Y-%m-%d')
    for group_name, group_url in groups.items():
        if group_name not in empty_groups.keys():
            try:
                update_existing_group(group_url, start_date=start_date, update_games=True)
            except Exception as e:
                LogUtils.log_error('Cannot update data for group: ' + group_url + ' ERROR: ' + str(e))
                traceback.print_exc()

    #For each new group, run: update_group_data from all time
    for group_url in empty_groups.values():
        try:
            update_existing_group(group_url)
        except Exception as e:
            LogUtils.log_error('Cannot update data for group: ' + group_url + ' ERROR: ' + str(e))
            traceback.print_exc()


def get_popular_giveaways(group_webpage, check_param, year_month, group_only_users=False, num_of_days=None):
    group = get_group_by_year_month(group_webpage, year_month)
    group_users = group.group_users.keys()
    giveaways_entries = dict()
    current_time = datetime.datetime.now()
    for giveaway, giveaway_data in group.group_giveaways.iteritems():
        giveaways_entries[giveaway_data] = 0
        # TotalEntries/EntriesOnFinish/EntriesWithinXDays
        if check_param == 'TotalEntries' or (check_param == 'EntriesOnFinish' and giveaway_data.has_winners()):
            for entry in giveaway_data.entries.values():
                if not group_only_users or entry.user_name in group_users:
                    giveaways_entries[giveaway_data] += 1
        elif check_param == 'EntriesWithinXDays' and num_of_days:
            if not giveaway_data.end_time:
                timedelta = current_time - giveaway_data.start_time
            else:
                timedelta = giveaway_data.end_time - giveaway_data.start_time

            if timedelta <= datetime.timedelta(days=num_of_days + 1):
                if giveaway_data not in giveaways_entries:
                    giveaways_entries[giveaway_data] = 0
                giveaways_entries[giveaway_data] += 1

    return giveaways_entries


def get_game_giveaways(group_webpage, game_name, start_time):
    group = MySqlConnector.load_group(group_webpage, limit_by_time=start_time, starts_after_str=start_time)
    if not group:
        return None
    group_users = group.group_users.keys()
    all_game_giveaways = dict()
    for group_giveaway in group.group_giveaways.values():
        group_game_name = group_giveaway.game_name.decode('utf-8')
        if not group_game_name:
            LogUtils.log_info("Invalid game name: " + group_giveaway.link)
        if group_game_name and (group_game_name.lower() in game_name.lower() or game_name.lower() in group_game_name.lower()):
            giveaway_entries = group_giveaway.entries.values()
            all_game_giveaways[group_giveaway] = len([entry for entry in giveaway_entries if entry.user_name in group_users])

    return all_game_giveaways


def update_all_db_users_data():
    #Load list of all groups & users from DB
    groups = get_groups_with_users()
    all_users = MySqlConnector.get_all_users()
    #Generate users list from all groups
    all_group_users = set()
    for group, group_data in groups.items():
        all_group_users.update(group_data.group_users)
    group_users = MySqlConnector.get_users_by_names(all_group_users)
    #Go over list, check if any changed
    changed_users = []
    deleted_users = [user for user in all_users if user.user_name not in all_group_users]
    for user in group_users.values():
        new_user = GroupUser(user.user_name)
        user_data_fetched = SteamGiftsScrapingUtils.update_user_additional_data(new_user)
        if new_user.steam_id:
            user_data_fetched &= SteamScrapingUtils.update_user_additional_data(new_user)
        if not user_data_fetched:
            deleted_users.append(user)
        elif not user.equals(new_user):
            changed_users.append(new_user)
    # Save changed users to the DB
    if changed_users:
        MySqlConnector.update_existing_users(changed_users)
    # Delete from DB users no longer on SteamGifts
    if deleted_users:
        MySqlConnector.delete_users(deleted_users)


def update_all_db_games_data():
    #Load all games from DB
    games = MySqlConnector.get_all_games()
    #Go over all games, and update their data
    changed_games = []
    removed_games = []
    for game_data in games:
        new_game_data = GameData(game_data.game_name, game_data.game_link, game_data.value)
        update_game_data(new_game_data)
        if game_data.num_of_reviews == -1 and game_data.steam_score == -1 and game_data.equals(new_game_data):
            removed_games.append(new_game_data)
        elif not game_data.equals(new_game_data):
            changed_games.append(new_game_data)
    # Save changed games to the DB
    if changed_games:
        MySqlConnector.update_existing_games(changed_games)
    # Delete from DB Games with no available data
    if removed_games:
        MySqlConnector.remove_games(removed_games)


def update_bundled_games_data():
    bundled_games_data = SteamGiftsScrapingUtils.get_bundled_games_data()

    if bundled_games_data:
        MySqlConnector.overwrite_bundled_games(bundled_games_data)


def get_group_by_year_month(group_webpage, year_month):
    split_date = year_month.split('-')
    year = int(split_date[0])
    month = int(split_date[1])
    month_start = year_month + '-01'
    if month == 12:
        month_end = str(year + 1) + '-01-01'
    else:
        month_end = str(year) + '-' + get_next_month(month) + '-01'
    group = MySqlConnector.load_group(group_webpage, limit_by_time=True, ends_after_str=month_start, ends_before_str=month_end)
    return group


def get_next_month(month):
    month += 1
    if month >= 10:
        return str(month)
    return '0' + str(month)