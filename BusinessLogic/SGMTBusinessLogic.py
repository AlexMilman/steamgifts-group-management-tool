import time
import pylru

import SGToolsScrapingUtils
from BusinessLogic import SteamGiftsScrapingUtils, SteamScrapingUtils
from BusinessLogic.SGToolsScrapingUtils import SGToolsScraper
from BusinessLogic.SteamGiftsScrapingUtils import SteamGiftsScraper
from BusinessLogic.SteamScrapingUtils import SteamScraper
from Data.Group import Group

# Internal business logic of different SGMT commands
# Copyright (C) 2017  Alex Milman


LRU_CACHE_SIZE = 10

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

# LRU cache used to hold data of last LRU_CACHE_SIZE groups. In order to cache the data and not retrieve it every time.
# Going forward need to consider using an external (persistent) cache server
groups = pylru.lrucache(LRU_CACHE_SIZE)
sgscraper = SteamGiftsScraper()
sgtoolsscraper = SGToolsScraper()
steamscraper = SteamScraper()




def missing_after_n_giveaway(group_webpage, n, steam_thread):
    load_group(group_webpage)
    load_group_user_steam_ids(group_webpage)
    group_data = groups[group_webpage]
    group_giveaways = group_data.group_giveaways
    group_users = group_data.group_users
    print 'group giveaways: ' + str(group_giveaways)
    print 'group users: ' + str(group_users)
    after_n_giveaways = steamscraper.verify_after_n_giveaways(steam_thread, group_giveaways, group_users.keys())
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
    after_n_giveaways = steamscraper.verify_after_n_giveaways(steam_thread, group_giveaways, group_users.keys())
    print 'after-n giveaways per user: ' + str(after_n_giveaways)
    for poster in after_n_giveaways:
        print 'User: ' + SteamGiftsScrapingUtils.get_user_link(poster) + ' Posted the following after-' + n + ' giveaways: ' + parse_list(after_n_giveaways[poster])


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
        print 'User: ' + SteamGiftsScrapingUtils.get_user_link(user) + ' Posted the following giveaways: ' + parse_list(giveaways_per_user[user])


def get_all_user_wins(group_webpage):
    load_group(group_webpage)
    wins = get_user_wins(groups[group_webpage])
    for winner in wins:
        print 'User: ' + SteamGiftsScrapingUtils.get_user_link(winner) + ' Won the following giveaways: ' + parse_list(wins[winner])


def get_stemagifts_to_steam_user_translation(group_webpage):
    load_group_users(group_webpage)
    steam_id_to_user = steamscraper.get_steam_id_to_user_dict(groups[group_webpage].group_users.values())
    for steam_profile_id, user in steam_id_to_user.iteritems():
        print 'Steamgifts User: ' + SteamGiftsScrapingUtils.get_user_link(user) + '.  Steam profile: ' + SteamScrapingUtils.steam_profile_link + steam_profile_id


def get_all_giveaways_in_group(group_webpage):
    load_group_giveaways(group_webpage)
    for giveaway in groups[group_webpage].group_giveaways.values():
        print 'Giveaway: ' + giveaway.link + '.  Created by: ' + SteamGiftsScrapingUtils.steamgifts_user_link + giveaway.creator \
              + '.  Won by: ' + parse_list(giveaway.winners, SteamGiftsScrapingUtils.steamgifts_user_link)


def get_all_users_in_group(group_webpage):
    users_list = sgscraper.get_group_users(group_webpage)
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
            print SteamGiftsScrapingUtils.get_user_link(user)


def get_month(datetime):
    return time.localtime(datetime).tm_mon


def get_users_with_negative_steamgifts_ratio(group_webpage):
    load_group_users(group_webpage)
    users_with_negative_ratio = sgscraper.checkUsersSteamgiftsRatio(groups[group_webpage].group_users.keys())
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

def get_user_entered_giveaways(group_webpage, giveaway, cookies, addition_date):
    if addition_date:
        giveaways = sgscraper.getGroupGiveawaysUserEntered(group_webpage, giveaway, cookies, user_addition_date=addition_date)
    else:
        giveaways = sgscraper.getGroupGiveawaysUserEntered(group_webpage, giveaway, cookies)
    for giveaway in giveaways:
        print giveaway


def user_check_rules(user, check_nonactivated=False, check_multiple_wins=False, check_real_cv_value=False, check_level=False, level=0):
    broken_rules = []
    if check_nonactivated and sgtoolsscraper.check_nonactivated(user):
        broken_rules.append('Has non-activated games: ' + SGToolsScrapingUtils.sgtools_check_nonactivated_link + user)

    if check_multiple_wins and sgtoolsscraper.check_multiple_wins(user):
        broken_rules.append('Has multiple wins: ' + SGToolsScrapingUtils.sgtools_check_multiple_wins_link + user)

    if check_real_cv_value and sgtoolsscraper.check_real_cv_value(user):
        broken_rules.append(
            'Won more than Sent. Won: ' + SGToolsScrapingUtils.sgtools_check_won_link + user + ', '
                               'Sent: ' + SGToolsScrapingUtils.sgtools_check_sent_link + user)

    if check_level and level > 0 and sgtoolsscraper.check_level(user, level):
        broken_rules.append('User level is less than 1: ' + SteamGiftsScrapingUtils.get_user_link(user))

    for message in broken_rules:
        print message


def test(cookies):
    SteamGiftsScraper().test(cookies)


def load_group(group_webpage, cookies=None):
    if group_webpage not in groups:
        group_users = sgscraper.get_group_users(group_webpage)
        group_giveaways = sgscraper.get_group_giveaways(group_webpage, cookies)
        groups[group_webpage] = Group(group_users, group_giveaways)


def load_group_users(group_webpage):
    if group_webpage not in groups:
        group_users = sgscraper.get_group_users(group_webpage)
        groups[group_webpage] = Group(group_users=group_users)
    elif groups[group_webpage].group_users:
        group_users = sgscraper.get_group_users(group_webpage)
        groups[group_webpage].group_users = group_users


def load_group_giveaways(group_webpage, cookies=None):
    if group_webpage not in groups:
        group_giveaways = sgscraper.get_group_giveaways(group_webpage, cookies)
        groups[group_webpage] = Group(group_giveaways=group_giveaways)
    elif groups[group_webpage].group_giveaways:
        group_giveaways = sgscraper.get_group_giveaways(group_webpage, cookies)
        groups[group_webpage].group_giveaways = group_giveaways


def load_group_user_steam_ids(group_webpage):
    if group_webpage in groups and groups[group_webpage].group_users:
        for user in groups[group_webpage].group_users.values():
            user.steam_id = steamscraper.get_user_steam_id(user.user_name)


def print_warranty():
    print 'This program is distributed in the hope that it will be useful,'
    print 'but WITHOUT ANY WARRANTY; without even the implied warranty of'
    print 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the'
    print 'GNU General Public License for more details.'


def print_conditions():
    print 'This program is free software: you can redistribute it and/or modify'
    print 'it under the terms of the GNU General Public License as published by'
    print 'the Free Software Foundation, either version 3 of the License, or'
    print '(at your option) any later version.'


def print_usage():
    print 'SteamGifts Group Management Tool (SGMT)  Copyright (C) 2017  Alex Milman'
    print 'This program comes with ABSOLUTELY NO WARRANTY; for details type \'GGTMStandalone.py -w\'.'
    print 'This is free software, and you are welcome to redistribute it'
    print 'under certain conditions; type \'GGTMStandalone.py -c\' for details.'
    print ''
    print '\t\t ' + printBold('Giftropolis Group Management Tool (GGMT) usage instructions')
    print 'GGTMStandalone.py -h - Show this screen'
    print 'GGTMStandalone.py -f <Feature Name> - Run one of the features below'
    print ''
    print 'Standard Features:'
    print '\t' + printBold('MissingAfterNGiveaway') + ' - Some groups require a member to create an exclusive group giveaway, after a number of times he won group giveaways. I call it an After-N giveaway.\n' \
          + '\tThis feature allows to check that all users adhere to this rule, and will printout a list of users that did not create/post enough giveaways, and their details.'
    print '\tSYNTAX: GGTMStandalone.py -f MissingAfterNGiveaway -w <steamgifts group webpage> -s <steam after-n giveaways thread> -n <number of GAs after which an exclusive GA is required>'
    print '\tEXAMPLE: GGTMStandalone.py -f MissingAfterNGiveaway -w https://www.steamgifts.com/group/AhzO3/giftropolis -s http://steamcommunity.com/groups/Giftropolis/discussions/0/355043117503501545 -n 3'
    print ''
    print '\t' + printBold('CheckMonthly') + ' - Returns a list of all users who didn\'t create a giveaway in a given month'
    print '\tSYNTAX: GGTMStandalone.py -f CheckMonthly -w <steamgifts group webpage> -m <Month number> -d <Minimum number of days of a GA>'
    print '\tEXAMPLE: GGTMStandalone.py -f CheckMonthly -w https://www.steamgifts.com/group/AhzO3/giftropolis -m 11 -d 3'
    print ''
    print '\t' + printBold('NegativeSteamgiftsRatio') + ' - Returns a list of all users who have a negative won/gifted ratio in SteamGifts'
    print '\tSYNTAX: GGTMStandalone.py -f NegativeSteamgiftsRatio -w <steamgifts group webpage>'
    print '\tEXAMPLE: GGTMStandalone.py -f NegativeSteamgiftsRatio -w https://www.steamgifts.com/group/AhzO3/giftropolis'
    print ''
    print '\t' + printBold('NegativeGroupRatio') + ' - Returns a list of all users who have a negative won/gifted ratio in the Group'
    print '\tSYNTAX: GGTMStandalone.py -f NegativeGroupRatio -w <steamgifts group webpage>'
    print '\tEXAMPLE: GGTMStandalone.py -f NegativeGroupRatio -w https://www.steamgifts.com/group/AhzO3/giftropolis'
    print ''
    print '\t' + printBold('UserCheckRules') + ' - Check if a user complies to group rules'
    print '\tSYNTAX: GGTMStandalone.py -f UserCheckRules -u <user name> -o <options seperated by :>'
    print '\tOptions are:'
    print '\t\tn - Check user doesn\'t have non activated games'
    print '\t\tm - Check user doesn\'t have multiple wins'
    print '\t\tr - Check user has positive real CV ratio'
    print '\t\tl+<level> - Check user is above certain level'
    print '\tEXAMPLE: GGTMStandalone.py -f UserCheckRules -u Mdk25 -o "n:m:r:l+1"'
    print ''
    print ''
    print 'Advanced Features:'
    print 'These features require operations which cannot be performed anonymously, you will be required to provide your personal cookies'
    print '\t' + printBold('UserEnteredGiveaways') + ' - For a given user, returns all group giveaways the user has entered since a given date.\n' \
          + '\tThis is helpfull in case of a new user, or a user in probation you want to verify is following the "no entering giveaways" rule.'
    print '\tSYNTAX: GGTMStandalone.py -f UserEnteredGiveaways -w <steamgifts group webpage> -u <steamgifts username> -a <date from which to start the check: YYYY-MM-DD> -c <your steamgifts cookies>'
    print '\tEXAMPLE: GGTMStandalone.py -f UserEnteredGiveaways -w https://www.steamgifts.com/group/AhzO3/giftropolis -u Oozyyy -a 2017-11-20 -c "_dm_sync=true; _dm_bid=true; ..."'
    print ''
    print ''
    print 'Basic Features:'
    print '\t' + printBold('GetAllUsersInGroup') + ' - Returns a list of all users in a given group'
    print '\tSYNTAX: GGTMStandalone.py -f GetAllUsersInGroup -w <steamgifts group webpage> '
    print '\tEXAMPLE: GGTMStandalone.py -f GetAllUsersInGroup -w https://www.steamgifts.com/group/AhzO3/giftropolis'
    print ''
    print '\t' + printBold('GetAllGiveawaysInGroup') + ' - Returns a list of all giveaways created in the group. Who created them, and who won them.'
    print '\tSYNTAX: GGTMStandalone.py -f GetAllGiveawaysInGroup -w <steamgifts group webpage> '
    print '\tEXAMPLE: GGTMStandalone.py -f GetAllGiveawaysInGroup -w https://www.steamgifts.com/group/AhzO3/giftropolis'
    print ''
    print '\t' + printBold('GetSteamGiftsUserToSteamUserTranslation') + ' - Returns a list of users in a given group, with a link to the Steam profile of each user'
    print '\tSYNTAX: GGTMStandalone.py -f GetSteamGiftsUserToSteamUserTranslation -w <steamgifts group webpage> '
    print '\tEXAMPLE: GGTMStandalone.py -f GetSteamGiftsUserToSteamUserTranslation -w https://www.steamgifts.com/group/AhzO3/giftropolis'
    print ''
    print '\t' + printBold('GetAllUserWins') + ' - Get for each user, all the giveaways he won in the group'
    print '\tSYNTAX: GGTMStandalone.py -f GetAllUserWins -w <steamgifts group webpage> '
    print '\tEXAMPLE: GGTMStandalone.py -f GetAllUserWins -w https://www.steamgifts.com/group/AhzO3/giftropolis'
    print ''
    print '\t' + printBold('GetAllUserGiveaways') + ' - Get for each user, all the giveaways he created in the group'
    print '\tSYNTAX: GGTMStandalone.py -f GetAllUserGiveaways -w <steamgifts group webpage> '
    print '\tEXAMPLE: GGTMStandalone.py -f GetAllUserGiveaways -w https://www.steamgifts.com/group/AhzO3/giftropolis'
    print ''
    print '\t' + printBold('GetAllAfterNGiveawaysPerUser') + ' - Get for each user, all the After-N giveaways he created'
    print '\tSYNTAX: GGTMStandalone.py -f GetAllAfterNGiveawaysPerUser -w <steamgifts group webpage> -s <steam after-n giveaways thread> -n <number of GAs after which an exclusive GA is required>'
    print '\tEXAMPLE: GGTMStandalone.py -f GetAllAfterNGiveawaysPerUser -w https://www.steamgifts.com/group/AhzO3/giftropolis -s http://steamcommunity.com/groups/Giftropolis/discussions/0/355043117503501545 -n 3'


def printBold(text):
    return BOLD + text + END

def parse_list(list, prefix=''):
    result = ''
    for item in list:
        result += prefix + item + ', '

    return result[:-2]


