import time
import pylru

from BusinessLogic.ScrapingUtils import SteamGiftsScrapingUtils, SGToolsScrapingUtils, SteamRepScrapingUtils, \
    SteamScrapingUtils, SGToolsConsts, SteamGiftsConsts, SteamRepConsts, SteamConsts
from BusinessLogic.Utils import WebUtils
from Data.Group import Group

# Internal business logic of different SGMT commands
# Copyright (C) 2017  Alex Milman


LRU_CACHE_SIZE = 10



# LRU cache used to hold data of last LRU_CACHE_SIZE groups. In order to cache the data and not retrieve it every time.
# Going forward need to consider using an external (persistent) cache server
groups = pylru.lrucache(LRU_CACHE_SIZE)


def missing_after_n_giveaway(group_webpage, n, steam_thread):
    load_group(group_webpage, load_additional_user_data=True)
    group_data = groups[group_webpage]
    group_giveaways = group_data.group_giveaways
    group_users = group_data.group_users
    print 'group giveaways: ' + str(group_giveaways)
    print 'group users: ' + str(group_users)
    after_n_giveaways = SteamScrapingUtils.verify_after_n_giveaways(steam_thread, group_giveaways, group_users.keys())
    print 'after-n giveaways per user: ' + str(after_n_giveaways)
    wins = get_user_wins(group_data)
    discrepancies = findDiscrepancies(n, wins, after_n_giveaways)
    print 'discrepancies per user: ' + str(discrepancies)


def get_user_wins(group_data):
    user_wins=dict()
    for giveaway in group_data.group_giveaways.values():
        for winner in giveaway.winners:
            if winner in group_data.group_users.keys():
                if winner not in user_wins:
                    user_wins[winner] = set()
                user_wins[winner].add(giveaway.link)
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
    load_group(group_webpage, load_additional_user_data=True)
    group_giveaways = groups[group_webpage].group_giveaways
    group_users = groups[group_webpage].group_users
    after_n_giveaways = SteamScrapingUtils.verify_after_n_giveaways(steam_thread, group_giveaways, group_users.keys())
    print 'after-n giveaways per user: ' + str(after_n_giveaways)
    for poster in after_n_giveaways:
        print 'User: ' + SteamGiftsConsts.get_user_link(poster) + ' Posted the following after-' + n + ' giveaways: ' + parse_list(after_n_giveaways[poster])


def get_all_user_giveaways(group_webpage):
    giveaways_per_user=dict()
    load_group(group_webpage)
    group_giveaways = groups[group_webpage].group_giveaways
    users = groups[group_webpage].group_users.keys()
    for giveaway in group_giveaways.values():
        poster = giveaway.creator
        if poster in users:
            if poster not in giveaways_per_user:
                giveaways_per_user[poster] = set()
            giveaways_per_user[poster].add(giveaway.link)

    for user in giveaways_per_user.keys():
        print 'User: ' + SteamGiftsConsts.get_user_link(user) + ' Posted the following giveaways: ' + parse_list(giveaways_per_user[user])


def get_all_user_wins(group_webpage):
    load_group(group_webpage)
    wins = get_user_wins(groups[group_webpage])
    for winner in wins:
        print 'User: ' + SteamGiftsConsts.get_user_link(winner) + ' Won the following giveaways: ' + parse_list(wins[winner])


def get_stemagifts_to_steam_user_translation(group_webpage):
    load_group_users(group_webpage)
    steam_id_to_user = SteamScrapingUtils.get_steam_id_to_user_dict(groups[group_webpage].group_users.values())
    for steam_profile_id, user in steam_id_to_user.iteritems():
        print 'Steamgifts User: ' + SteamGiftsConsts.get_user_link(user) + '.  Steam profile: ' + SteamConsts.STEAM_PROFILE_LINK + steam_profile_id


def get_all_giveaways_in_group(group_webpage):
    load_group_giveaways(group_webpage)
    for giveaway in groups[group_webpage].group_giveaways.values():
        print 'Giveaway: ' + giveaway.link + '.  Created by: ' + SteamGiftsConsts.STEAMGIFTS_USER_LINK + giveaway.creator \
              + '.  Won by: ' + parse_list(giveaway.winners, SteamGiftsConsts.STEAMGIFTS_USER_LINK)


def get_all_users_in_group(group_webpage):
    users_list = SteamGiftsScrapingUtils.get_group_users(group_webpage)
    for user in users_list:
        print user


def check_monthly(group_webpage, year_month, cookies, min_days=0, min_game_value=0.0, min_steam_num_of_reviews=0, min_steam_score=0):
    load_group(group_webpage, cookies, earliest_date=year_month + '-01')
    users = groups[group_webpage].group_users.keys()
    monthly_posters = set()
    monthly_unfinished = dict()
    month = int(year_month.split('-')[1])
    for group_giveaway in groups[group_webpage].group_giveaways.values():
        end_month = group_giveaway.end_date.tm_mon
        start_month = group_giveaway.start_date.tm_mon
        # If GA started in previous month, mark it as started on the 1th of the month
        if start_month == month - 1 and end_month == month:
            start_day = 1
            start_month = month
        else:
            start_day = group_giveaway.start_date.tm_mday
        end_day = group_giveaway.end_date.tm_mday
        if group_giveaway.creator in users and len(group_giveaway.groups) == 1\
                and start_month == month and end_month == month\
                and end_day - start_day >= min_days\
                and (min_game_value == 0 or group_giveaway.value >= min_game_value):
            if check_steam_reviews(group_giveaway.link, cookies, min_steam_num_of_reviews, min_steam_score):
                if len(group_giveaway.winners) > 0:
                    monthly_posters.add(group_giveaway.creator)
                else:
                    if group_giveaway.creator not in monthly_unfinished:
                        monthly_unfinished[group_giveaway.creator] = set()
                    monthly_unfinished[group_giveaway.creator].add(group_giveaway.link)

    print '\nUsers with unfinished monthly GAs:'
    for user,links in monthly_unfinished.iteritems():
        print 'User ' + SteamGiftsConsts.get_user_link(user) + ' giveaways: ' + parse_list(links)

    print '\nUsers without monthly giveaways:'
    for user in users:
        if user not in monthly_posters and user not in monthly_unfinished.keys():
            print SteamGiftsConsts.get_user_link(user)


def check_steam_reviews(giveaway_link, cookies, min_steam_num_of_reviews, min_steam_score):
    num_of_reviews = 0
    steam_score = 0
    if min_steam_num_of_reviews != 0 or min_steam_score != 0:
        steam_game_link = SteamGiftsScrapingUtils.get_steam_game_link(giveaway_link, cookies)
        if steam_game_link:
            num_of_reviews, steam_score = SteamScrapingUtils.get_steam_game_data(steam_game_link)
    return (min_steam_num_of_reviews == 0 or (num_of_reviews != 0 and min_steam_num_of_reviews <= num_of_reviews)) \
           and (min_steam_score == 0 or (steam_score != 0 and min_steam_score <= steam_score))


def get_users_with_negative_steamgifts_ratio(group_webpage):
    load_group_users(group_webpage, load_additional_data=True)
    for group_user in groups[group_webpage].group_users.values():
        if group_user.global_won > group_user.global_sent:
            print group_user.user_name


def get_users_with_negative_group_ratio(group_webpage):
    users_with_negative_ratio=[]
    load_group_users(group_webpage)
    for user in groups[group_webpage].group_users.values():
        if user.group_won > user.group_sent:
            users_with_negative_ratio.append(user.user_name)

    for user in users_with_negative_ratio:
        print user

#TODO: Add giveaway entered time (from entries page)
def get_user_entered_giveaways(group_webpage, users, cookies, addition_date):
    load_group_giveaways(group_webpage, cookies, addition_date)
    users_list = users.split(',')
    for group_giveaway in groups[group_webpage].group_giveaways.values():
        # Go over all giveaways not closed before "addition_date"
        if not addition_date or addition_date < time.strftime('%Y-%m-%d', group_giveaway.end_date):
            for user in users_list:
                if user in group_giveaway.entries:
                    print 'User ' + user + ' entered giveaway: ' + group_giveaway.link

#TODO: Add checking user didn't enter any giveaways
def check_user_first_giveaway(group_webpage, users, cookies, addition_date=None, days_to_create_ga=0, min_ga_time=0,
                              min_game_value=0.0, min_steam_num_of_reviews=0, min_steam_score=0):
    load_group_giveaways(group_webpage, cookies, earliest_date=addition_date)
    users_list = users.split(',')
    for group_giveaway in groups[group_webpage].group_giveaways.values():
        if (  group_giveaway.creator in users_list
            and
                len(group_giveaway.groups) == 1
            and
                ((not addition_date or days_to_create_ga == 0)
                or (addition_date and days_to_create_ga > 0 and group_giveaway.start_date.tm_mday <= int(addition_date.split('-')[2]) + days_to_create_ga))
            and
                (min_ga_time == 0
                or (min_ga_time > 0 and group_giveaway.end_date.tm_mday - group_giveaway.start_date.tm_mday >= min_ga_time))
            and
                (min_game_value == 0 or group_giveaway.value > min_game_value)):
            if check_steam_reviews(group_giveaway.link, cookies, min_steam_num_of_reviews, min_steam_score):
                print 'User ' + group_giveaway.creator + ' first giveaway: ' + group_giveaway.link


def user_check_rules(user, check_nonactivated=False, check_multiple_wins=False, check_real_cv_value=False, check_level=False, level=0, check_steamrep=False):
    broken_rules = []
    if check_nonactivated and SGToolsScrapingUtils.check_nonactivated(user):
        broken_rules.append('Has non-activated games: ' + SGToolsConsts.SGTOOLS_CHECK_NONACTIVATED_LINK + user)

    if check_multiple_wins and SGToolsScrapingUtils.check_multiple_wins(user):
        broken_rules.append('Has multiple wins: ' + SGToolsConsts.SGTOOLS_CHECK_MULTIPLE_WINS_LINK + user)

    if check_real_cv_value and SGToolsScrapingUtils.check_real_cv_value(user):
        broken_rules.append(
            'Won more than Sent. Won: ' + SGToolsConsts.SGTOOLS_CHECK_WON_LINK + user + ', '
                               'Sent: ' + SGToolsConsts.SGTOOLS_CHECK_SENT_LINK + user)

    if check_level and level > 0 and SGToolsScrapingUtils.check_level(user, level):
        broken_rules.append('User level is less than ' + str(level) + ': ' + SteamGiftsConsts.get_user_link(user))

    if check_steamrep:
        user_steam_id = SteamGiftsScrapingUtils.get_user_steam_id(user)
        if user_steam_id and not SteamRepScrapingUtils.check_user_not_public_or_banned(user_steam_id):
            broken_rules.append('User ' + SteamGiftsConsts.get_user_link(user)
                                + ' is not public or banned: ' + SteamRepConsts.get_steamrep_link(user_steam_id))

    for message in broken_rules:
        print message


def test(group_webpage):
    WebUtils.get_page_content('https://www.steamgifts.com/giveaway/McKde/strider-sutoraida-fei-long', '_ga=GA1.2.1681724704.1509967278; _gid=GA1.2.1634724628.1512244833')
    pass


def load_group(group_webpage, cookies=None, earliest_date=None, load_additional_user_data=False):
    if group_webpage not in groups:
        group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage, load_additional_user_data)
        group_giveaways = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies, earliest_date)
        groups[group_webpage] = Group(group_users, group_giveaways)


def load_group_users(group_webpage, load_additional_data=False):
    if group_webpage not in groups or groups[group_webpage].group_users is None:
        group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage)
        # Additional Data = Steam ID, SG total won, SG total sent
        if load_additional_data:
            for group_user in group_users:
                SteamGiftsScrapingUtils.update_user_additional_data(group_user)
        if group_webpage not in groups:
            groups[group_webpage] = Group(group_users=group_users)
        else:
            groups[group_webpage].group_users = group_users


def load_group_giveaways(group_webpage, cookies=None, earliest_date=None):
    if group_webpage not in groups:
        group_giveaways = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies, earliest_date)
        groups[group_webpage] = Group(group_giveaways=group_giveaways)
    elif groups[group_webpage].group_giveaways is None:
        group_giveaways = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies, earliest_date)
        groups[group_webpage].group_giveaways = group_giveaways


def parse_list(list, prefix=''):
    result = ''
    for item in list:
        result += prefix + item + ', '

    return result[:-2]


