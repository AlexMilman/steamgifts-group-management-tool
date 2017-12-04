import getopt
import sys

from BusinessLogic import SGMTBusinessLogic


# Standalone CLI implementation of the SGMT functionality
# Copyright (C) 2017  Alex Milman

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


def main(argv):
    if argv is None:
        argv = sys.argv
    feature = ''
    group_webpage = ''
    steam_thread = ''
    n = ''
    year_month = ''
    user = ''
    cookies = ''
    addition_date = None
    max_pages = 0
    show_warranty=False
    show_conditions=False
    check_nonactivated=False
    check_multiple_wins=False
    check_real_cv_value=False
    check_level=False
    level=0
    check_steamrep=False
    days=0
    min_time=0
    min_game_value=0.0
    min_steam_num_of_reviews=0
    min_steam_score=0
    try:
        opts, args = getopt.getopt(argv, "whf:g:s:n:m:p:u:c:a:o:d:t:v:r:", [])
    except getopt.GetoptError:
        print 'INVALID COMMAND: GGTMStandalone.py ' +  argv + '\n'
        print_usage()
        sys.exit(2)
    if not opts:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt == "-f":
            feature = arg
        elif opt == "-g":
            group_webpage = arg
        elif opt == "-s":
            steam_thread = arg
        elif opt == "-m":
            year_month = arg
        elif opt == "-p":
            max_pages = int(arg)
            min_steam_score = int(arg)
        elif opt == "-u":
            user = arg
        elif opt == "-n":
            n = arg
        elif opt == "-c":
            cookies = arg
        elif opt == "-a":
            addition_date = arg
        elif opt == "-o":
            for option in arg.split(':'):
                if option == 'n':
                    check_nonactivated = True
                elif option == 'm':
                    check_multiple_wins = True
                elif option == 'r':
                    check_real_cv_value = True
                elif option.startswith('l'):
                    check_level = True
                    level = int(option.split('+')[1])
                elif option == 's':
                    check_steamrep = True
        elif opt == "-w":
            show_warranty = True
        elif opt == "-c" and not arg:
            show_conditions = True
        elif opt == "-d":
            days = int(arg)
        elif opt == "-v":
            min_game_value = float(arg)
        elif opt == "-r":
            min_steam_num_of_reviews = int(arg)

    if show_warranty:
        print_warranty()
        sys.exit(0)

    if show_conditions:
        print_conditions()
        sys.exit(0)

    if feature == 'MissingAfterNGiveaway':
        SGMTBusinessLogic.missing_after_n_giveaway(group_webpage, n, steam_thread)
    elif feature == 'CheckMonthly':
        SGMTBusinessLogic.check_monthly(group_webpage, year_month, cookies, days)
    elif feature == 'GetAllUsersInGroup':
        SGMTBusinessLogic.get_all_users_in_group(group_webpage)
    elif feature == 'GetAllGiveawaysInGroup':
        SGMTBusinessLogic.get_all_giveaways_in_group(group_webpage)
    elif feature == 'GetSteamGiftsUserToSteamUserTranslation':
        SGMTBusinessLogic.get_stemagifts_to_steam_user_translation(group_webpage)
    elif feature == 'GetAllUserWins':
        SGMTBusinessLogic.get_all_user_wins(group_webpage)
    elif feature == 'GetAllUserGiveaways':
        SGMTBusinessLogic.get_all_user_giveaways(group_webpage)
    elif feature == 'GetAllAfterNGiveawaysPerUser':
        SGMTBusinessLogic.get_all_after_n_giveaways_per_user(group_webpage, n, steam_thread)
    elif feature == 'NegativeSteamgiftsRatio':
        SGMTBusinessLogic.get_users_with_negative_steamgifts_ratio(group_webpage)
    elif feature == 'NegativeGroupRatio':
        SGMTBusinessLogic.get_users_with_negative_group_ratio(group_webpage)
    elif feature == 'UserEnteredGiveaways':
        SGMTBusinessLogic.get_user_entered_giveaways(group_webpage, user, cookies, addition_date)
    elif feature == 'UserCheckRules':
        SGMTBusinessLogic.user_check_rules(user, check_nonactivated, check_multiple_wins, check_real_cv_value, check_level, level, check_steamrep)
    elif feature == 'UserCheckFirstGiveaway':
        SGMTBusinessLogic.check_user_first_giveaway(group_webpage, user, cookies, addition_date, days, min_time, min_game_value, min_steam_num_of_reviews, min_steam_score)
    elif feature == 'Test':
        SGMTBusinessLogic.test(group_webpage)
    else:
        print 'INVALID FEATURE: ' +  feature + '\n'
        print_usage()
        sys.exit(2)



    #TODO Optional: max_pages - ???
    #TODO Optional: ignore_users

    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])


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
    print '\t' + printBold('GetAllAfterNGiveawaysPerUser') + ' - Get for each user, all the After-N giveaways he created'
    print '\tSYNTAX: GGTMStandalone.py -f GetAllAfterNGiveawaysPerUser -w <steamgifts group webpage> -s <steam after-n giveaways thread> -n <number of GAs after which an exclusive GA is required>'
    print '\tEXAMPLE: GGTMStandalone.py -f GetAllAfterNGiveawaysPerUser -w https://www.steamgifts.com/group/AhzO3/giftropolis -s http://steamcommunity.com/groups/Giftropolis/discussions/0/355043117503501545 -n 3'
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
    print '\t\ts - Check user has no SteamRep bans and his profile is public'
    print '\t\tl+<level> - Check user is above certain level'
    print '\tEXAMPLE: GGTMStandalone.py -f UserCheckRules -u Mdk25 -o "n:m:r:s:l+1"'
    print ''
    print ''
    print 'Advanced Features:'
    print 'These features require operations which cannot be performed anonymously, you will be required to provide your personal cookies'
    print '\t' + printBold('UserEnteredGiveaways') + ' - For a given user, returns all group giveaways the user/s has entered since a given date.\n' \
          + '\tThis is helpfull in case of a new user, or a user in probation you want to verify is following the "no entering giveaways" rule.'
    print '\tSYNTAX: GGTMStandalone.py -f UserEnteredGiveaways -w <steamgifts group webpage> -u <steamgifts username or list of users separated by column> -a <date from which to start the check: YYYY-MM-DD> -c <your steamgifts cookies>'
    print '\tEXAMPLE: GGTMStandalone.py -f UserEnteredGiveaways -w https://www.steamgifts.com/group/AhzO3/giftropolis -u Oozyyy,7Years -a 2017-11-20 -c "_dm_sync=true; _dm_bid=true; ..."'
    print ''
    print '\t' + printBold('UserCheckFirstGiveaway') + ' - Check if a user complies with first giveaway rules:\n' \
          + '\tCreates a giveaway unique to the group. Creates the giveaway within X days of entering the group. Creates the giveaway for a minimum of X days.'
    print '\tSYNTAX: GGTMStandalone.py -f UserCheckFirstGiveaway -w <steamgifts group webpage> -u <steamgifts username> -c <your steamgifts cookies> \n'\
          + '\t(Optional:) -a <date from which the user entered the group: YYYY-MM-DD> -d <within how many days since entering the group should the GA be created (in days)> -t <min GA running time (in days)>'\
          + '\t -v <Minimal game value (in $) allowed> -r <Minimal number of Steam reviews allowed for a game> -p <Minimal Steam score allowed for a game>'
    print '\tEXAMPLE: GGTMStandalone.py -f UserCheckFirstGiveaway -w https://www.steamgifts.com/group/AhzO3/giftropolis -u Oozyyy -c "_dm_sync=true; _dm_bid=true; ..." -a 2017-11-20 -d 2 -t 7 -v 9.95 -r 100 -p 80'
    print ''
    print '\t' + printBold('CheckMonthly') + ' - Returns a list of all users who didn\'t create a giveaway in a given month'
    print '\tSYNTAX: GGTMStandalone.py -f CheckMonthly -w <steamgifts group webpage> -m <Year+Month> -d <Minimum number of days of a GA>'
    print '\tEXAMPLE: GGTMStandalone.py -f CheckMonthly -w https://www.steamgifts.com/group/AhzO3/giftropolis -m 2017-11 -d 3'
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


def printBold(text):
    return BOLD + text + END
