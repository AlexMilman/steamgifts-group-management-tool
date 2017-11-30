import time
import pylru

from BusinessLogic.ScrapingUtils import SteamGiftsScrapingUtils, SGToolsScrapingUtils, SteamRepScrapingUtils, \
    SteamScrapingUtils, SGToolsConsts, SteamGiftsConsts, SteamRepConsts, SteamConsts
from Data.Group import Group

# Internal business logic of different SGMT commands
# Copyright (C) 2017  Alex Milman


LRU_CACHE_SIZE = 10



# LRU cache used to hold data of last LRU_CACHE_SIZE groups. In order to cache the data and not retrieve it every time.
# Going forward need to consider using an external (persistent) cache server
groups = pylru.lrucache(LRU_CACHE_SIZE)


def missing_after_n_giveaway(group_webpage, n, steam_thread):
    load_group(group_webpage)
    load_group_user_steam_ids(group_webpage)
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
    load_group(group_webpage)
    load_group_user_steam_ids(group_webpage)
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


def check_monthly(group_webpage, month, cookies, min_days=0):
    load_group(group_webpage, cookies)
    users = groups[group_webpage].group_users.keys()
    monthly_posters = set()
    for group_ga in groups[group_webpage].group_giveaways.values():
        if group_ga.creator in users and len(group_ga.groups) == 1 and len(group_ga.winners) > 0\
                and group_ga.start_date.tm_mon == month and group_ga.end_date.tm_mon == month\
                and group_ga.end_date.tm_mday - group_ga.start_date.tm_mday >= min_days:
            monthly_posters.add(group_ga.creator)

    # users_list = DemoValues.get_demo_users()
    # monthly_posters = DemoValues.get_demo_posters()
    for user in users:
        if user not in monthly_posters:
            print SteamGiftsConsts.get_user_link(user)


def get_month(datetime):
    return time.localtime(datetime).tm_mon


def get_users_with_negative_steamgifts_ratio(group_webpage):
    load_group_users(group_webpage)
    users_with_negative_ratio = SteamGiftsScrapingUtils.check_users_steamgifts_ratio(groups[group_webpage].group_users.keys())
    for user in users_with_negative_ratio:
        print user

def get_users_with_negative_group_ratio(group_webpage):
    users_with_negative_ratio=[]
    load_group_users(group_webpage)
    for user in groups[group_webpage].group_users.values():
        if user.won_games > user.sent_games:
            users_with_negative_ratio.append(user.user_name)

    for user in users_with_negative_ratio:
        print user

def get_user_entered_giveaways(group_webpage, user, cookies, addition_date):
    load_group_giveaways(group_webpage, cookies)
    giveaways = SteamGiftsScrapingUtils.get_group_giveaways_user_entered(groups[group_webpage].group_giveaways.values(), user, cookies, addition_date)
    for giveaway in giveaways:
        print giveaway


def check_user_first_giveaway(group_webpage, user, cookies, addition_date, days_to_create_ga, min_ga_time):
    load_group_giveaways(group_webpage, cookies)
    giveaway = SteamGiftsScrapingUtils.check_user_fist_giveaway(groups[group_webpage].group_giveaways.values(), user, addition_date, days_to_create_ga, min_ga_time)
    print 'User\'s first giveaway: ' + str(giveaway)


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
    load_group_users(group_webpage)
    for user in groups[group_webpage].group_users.keys():
        user_check_rules(user, check_steamrep=True)



def load_group(group_webpage, cookies=None):
    if group_webpage not in groups:
        group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage)
        group_giveaways = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies)
        groups[group_webpage] = Group(group_users, group_giveaways)


def load_group_users(group_webpage):
    if group_webpage not in groups:
        group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage)
        groups[group_webpage] = Group(group_users=group_users)
    elif groups[group_webpage].group_users:
        group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage)
        groups[group_webpage].group_users = group_users


def load_group_giveaways(group_webpage, cookies=None):
    if group_webpage not in groups:
        group_giveaways = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies)
        groups[group_webpage] = Group(group_giveaways=group_giveaways)
    elif groups[group_webpage].group_giveaways:
        group_giveaways = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies)
        groups[group_webpage].group_giveaways = group_giveaways


def load_group_user_steam_ids(group_webpage):
    if group_webpage in groups and groups[group_webpage].group_users:
        for user in groups[group_webpage].group_users.values():
            user.steam_id = SteamGiftsScrapingUtils.get_user_steam_id(user.user_name)



def parse_list(list, prefix=''):
    result = ''
    for item in list:
        result += prefix + item + ', '

    return result[:-2]


