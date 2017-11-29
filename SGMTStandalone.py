import getopt
import sys

from BusinessLogic import SGMTBusinessLogic


# Standalone CLI implementation of the SGMT functionality
# Copyright (C) 2017  Alex Milman

def main(argv):
    if argv is None:
        argv = sys.argv
    feature = ''
    group_webpage = ''
    steam_thread = ''
    n = ''
    month = ''
    user = ''
    cookies = ''
    addition_date = None
    max_pages = 0
    print_warranty=False
    print_conditions=False
    check_nonactivated=False
    check_multiple_wins=False
    check_real_cv_value=False
    check_level=False
    level=0
    check_steamrep=False
    days=0
    min_time=0
    try:
        opts, args = getopt.getopt(argv, "whf:g:s:n:m:p:u:c:a:o:d:t:", [])
    except getopt.GetoptError:
        print 'INVALID COMMAND: GGTMStandalone.py ' +  argv + '\n'
        SGMTBusinessLogic.print_usage()
        sys.exit(2)
    if not opts:
        SGMTBusinessLogic.print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            SGMTBusinessLogic.print_usage()
            sys.exit()
        elif opt == "-f":
            feature = arg
        elif opt == "-g":
            group_webpage = arg
        elif opt == "-s":
            steam_thread = arg
        elif opt == "-m":
            month = int(arg)
        elif opt == "-p":
            max_pages = int(arg)
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
                    level = option.split('+')[1]
                elif option == 's':
                    check_steamrep = True
        elif opt == "-w":
            print_warranty = True
        elif opt == "-c" and not arg:
            print_conditions = True
        elif opt == "-d":
            days = arg
        elif opt == "-t":
            min_time = arg

    if print_warranty:
        SGMTBusinessLogic.print_warranty()
        sys.exit(0)

    if print_conditions:
        SGMTBusinessLogic.print_conditions()
        sys.exit(0)

    if feature == 'MissingAfterNGiveaway':
        SGMTBusinessLogic.missing_after_n_giveaway(group_webpage, n, steam_thread)
    elif feature == 'CheckMonthly':
        SGMTBusinessLogic.check_monthly(group_webpage, month, cookies, days)
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
        SGMTBusinessLogic.check_user_first_giveaway(group_webpage, user , cookies, addition_date, days, min_time)
    elif feature == 'Test':
        SGMTBusinessLogic.test(group_webpage)
    else:
        print 'INVALID FEATURE: ' +  feature + '\n'
        SGMTBusinessLogic.print_usage()
        sys.exit(2)



    #TODO Optional: max_pages - ???
    #TODO Optional: ignore_users

    #TODO: Add python dependencies file

    sys.exit(0)




if __name__ == "__main__":
    main(sys.argv[1:])
