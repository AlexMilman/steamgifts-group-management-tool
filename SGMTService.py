#!flask/bin/python
# API Service of SGMT
# Copyright (C) 2017  Alex Milman

import json
import time

import datetime
from flask import Flask
from flask import request

from BusinessLogic import SGMTBusinessLogic
from BusinessLogic.Utils import LogUtils
from Output import HtmlResponseGenerationService, HtmlUIGenerationService

app = Flask(__name__)


@app.route('/SGMT/', methods=['GET'])
def main_page():
    return HtmlUIGenerationService.generate_main_page_ui()


@app.route('/SGMT/CheckMonthlyUI', methods=['GET'])
def check_monthly_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.generate_check_monthly_ui(groups)
    return response


@app.route('/SGMT/CheckMonthly', methods=['GET'])
def check_monthly():
    group_webpage = request.args.get('group_webpage')
    year_month = request.args.get('year_month')
    year = request.args.get('year')
    month = request.args.get('month')
    if not year_month and year and month:
        year_month = year + '-' + month
    min_days = get_optional_int_param('min_days')
    min_entries = get_optional_int_param('min_entries')
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')
    alt_min_game_value = get_optional_float_param('alt_min_game_value')
    alt_min_steam_num_of_reviews = get_optional_int_param('alt_min_steam_num_of_reviews')
    alt_min_steam_score = get_optional_int_param('alt_min_steam_score')
    alt2_min_game_value = get_optional_float_param('alt2_min_game_value')
    alt2_min_steam_num_of_reviews = get_optional_int_param('alt2_min_steam_num_of_reviews')
    alt2_min_steam_score = get_optional_int_param('alt2_min_steam_score')
    min_entries_override = get_optional_int_param('min_entries_override')
    ignore_inactive_users = request.args.get('ignore_inactive_users')
    ignore_cakeday_users = request.args.get('ignore_cakeday_users')

    if not group_webpage or not year_month:
        return 'CheckMonthly - Returns a list of all users who didn\'t create a giveaway in a given month<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               'year_month=YYYY-MM Year+Month for which you want to check  <BR>' \
               '<B>Optional Params:</B> <BR>' \
               'min_days - Minimum number of days of a GA<BR>' \
               'min_entries - Minimum number entries when GA ends<BR>' \
               'min_game_value - Minimal game value (in $) allowed<BR>' \
               'min_steam_num_of_reviews - Minimal number of Steam reviews allowed for a game<BR>' \
               'min_steam_score - Minimal Steam score allowed for a game<BR>' \
               'alt_min_game_value - Alternative minimal game value (in $) allowed<BR>' \
               'alt_min_steam_num_of_reviews - Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt_min_steam_score - Alternative Minimal Steam score allowed for a game<BR>' \
               'alt2_min_game_value - 2nd Alternative minimal game value (in $) allowed<BR>' \
               'alt2_min_steam_num_of_reviews - 2nd Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt2_min_steam_score - 2nd Alternative Minimal Steam score allowed for a game<BR>' \
               'min_entries_override - Minimal number of entries to ignore score/value requirements<BR>' \
               'ignore_incative_users - Ignore inactive users (users who did not enter any GA this month)<BR>' \
               'ignore_cakeday_users - Ignore users who have a cakeday at the specified month<BR>' \
               '<BR>' \
               '<A HREF="/SGMT/CheckMonthly?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&year_month=2017-11&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80">Request Example</A>'

    users, monthly_posters, monthly_unfinished, inactive_users, cakeday_users = SGMTBusinessLogic.check_monthly(group_webpage, year_month, min_days, min_entries, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score, alt2_min_game_value, alt2_min_steam_num_of_reviews, alt2_min_steam_score, min_entries_override, ignore_inactive_users, ignore_cakeday_users)
    response = HtmlResponseGenerationService.generate_check_monthly_response(group_webpage, users, monthly_posters, monthly_unfinished, inactive_users, cakeday_users, year_month)
    return response


@app.route('/SGMT/CheckAllGiveawaysAccordingToRulesUI', methods=['GET'])
def check_all_giveaways_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.generate_check_all_giveaways_ui(groups)
    return response


@app.route('/SGMT/CheckAllGiveawaysAccordingToRules', methods=['GET'])
def check_all_giveaways():
    group_webpage = request.args.get('group_webpage')
    start_date = request.args.get('start_date')
    min_days = get_optional_int_param('min_days')
    min_entries = get_optional_int_param('min_entries')
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')
    alt_min_game_value = get_optional_float_param('alt_min_game_value')
    alt_min_steam_num_of_reviews = get_optional_int_param('alt_min_steam_num_of_reviews')
    alt_min_steam_score = get_optional_int_param('alt_min_steam_score')
    alt2_min_game_value = get_optional_float_param('alt2_min_game_value')
    alt2_min_steam_num_of_reviews = get_optional_int_param('alt2_min_steam_num_of_reviews')
    alt2_min_steam_score = get_optional_int_param('alt2_min_steam_score')
    free_group_only = request.args.get('free_group_only')

    if not group_webpage:
        return 'CheckAllGiveawaysAccordingToRules - Returns a list of all giveaways which were created not according to the rules<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               '<B>Optional Params:</B> <BR>' \
               'start_date=YYYY-MM-DD Start date from which to check giveaways <BR>' \
               'min_days - Minimum number of days of a GA<BR>' \
               'min_entries - Minimum number entries when GA ends<BR>' \
               'min_game_value - Minimal game value (in $) allowed<BR>' \
               'min_steam_num_of_reviews - Minimal number of Steam reviews allowed for a game<BR>' \
               'min_steam_score - Minimal Steam score allowed for a game<BR>' \
               'alt_min_game_value - Alternative minimal game value (in $) allowed<BR>' \
               'alt_min_steam_num_of_reviews - Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt_min_steam_score - Alternative Minimal Steam score allowed for a game<BR>' \
               'alt2_min_game_value - Alternative #2 minimal game value (in $) allowed<BR>' \
               'alt2_min_steam_num_of_reviews - Alternative #2 minimal number of Steam reviews allowed for a game<BR>' \
               'alt2_min_steam_score - Alternative #2 Minimal Steam score allowed for a game<BR>' \
               'free_group_only - Limit giveaways of free games to be group-only<BR>' \
               '<BR>' \
               '<A HREF="/SGMT/CheckAllGiveawaysAccordingToRules?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&start_date=2017-11-01&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80">Request Example</A>'

    invalid_giveaways, free_games, games = SGMTBusinessLogic.check_giveaways_valid(group_webpage, start_date, min_days, min_entries, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score, alt2_min_game_value, alt2_min_steam_num_of_reviews, alt2_min_steam_score, free_group_only)
    response = HtmlResponseGenerationService.generate_invalid_giveaways_response(games, invalid_giveaways, free_games)
    return response


@app.route('/SGMT/UserCheckFirstGiveawayUI', methods=['GET'])
def user_check_first_giveaway_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.generate_user_check_first_giveaway_ui(groups)
    return response


@app.route('/SGMT/UserCheckFirstGiveaway', methods=['GET'])
def user_check_first_giveaway():
    group_webpage = request.args.get('group_webpage')
    users = request.args.get('users')
    addition_date = request.args.get('addition_date')
    days_to_create_ga = get_optional_int_param('days_to_create_ga')
    min_entries = get_optional_int_param('min_entries')
    min_ga_time = get_optional_int_param('min_ga_time')
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')
    alt_min_game_value = get_optional_float_param('alt_min_game_value')
    alt_min_steam_num_of_reviews = get_optional_int_param('alt_min_steam_num_of_reviews')
    alt_min_steam_score = get_optional_int_param('alt_min_steam_score')
    alt2_min_game_value = get_optional_float_param('alt2_min_game_value')
    alt2_min_steam_num_of_reviews = get_optional_int_param('alt2_min_steam_num_of_reviews')
    alt2_min_steam_score = get_optional_int_param('alt2_min_steam_score')
    check_entered_giveaways = request.args.get('check_entered_giveaways')

    if not group_webpage or not users or not addition_date:
        return 'UserCheckFirstGiveaway  - Check if users comply with first giveaway rules:<BR>' \
                'For Example: Creates a giveaway unique to the group. Creates the giveaway within X days of entering the group. Creates the giveaway for a minimum of X days. Etc.<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               'users - A list of SteamGifts users (seperated by commas) <BR>' \
               'addition_date=YYYY-MM-DD - The date from which the user was added to the group <BR>' \
               '<B>Optional Params:</B> <BR>' \
               'days_to_create_ga - Within how many days of entering the group should the first GA be created<BR>' \
               'min_entries - Minimum number of entries when GA ends<BR>' \
               'min_ga_time - Minimum number of days of a GA to run<BR>' \
               'min_game_value - Minimal game value (in $) allowed<BR>' \
               'min_steam_num_of_reviews - Minimal number of Steam reviews allowed for a game<BR>' \
               'min_steam_score - Minimal Steam score allowed for a game<BR>' \
               'alt_min_game_value - Alternative minimal game value (in $) allowed<BR>' \
               'alt_min_steam_num_of_reviews - Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt_min_steam_score - Alternative Minimal Steam score allowed for a game<BR>' \
               'alt2_min_game_value - 2nd Alternative minimal game value (in $) allowed<BR>' \
               'alt2_min_steam_num_of_reviews - 2nd Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt2_min_steam_score - 2nd Alternative Minimal Steam score allowed for a game<BR>' \
               'check_entered_giveaways=True/False - Check if user entered any group GAs while his first GA is active<BR>' \
               '<BR>' \
               '<A HREF="/SGMT/UserCheckFirstGiveaway?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&users=Vlmbcn,7Years&addition_date=2017-12-01&days_to_create_ga=2&min_ga_time=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80&check_entered_giveaways=True">Request Example</A>'

    user_first_giveaway, succesfully_ended, user_no_giveaway, user_entered_giveaway, time_to_create_over = SGMTBusinessLogic.check_user_first_giveaway(group_webpage, users, addition_date, days_to_create_ga, min_ga_time, min_entries, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score, alt2_min_game_value, alt2_min_steam_num_of_reviews, alt2_min_steam_score, check_entered_giveaways)
    response = HtmlResponseGenerationService.generate_check_user_first_giveaway_response(user_first_giveaway, succesfully_ended, user_no_giveaway, user_entered_giveaway, time_to_create_over)
    return response


@app.route('/SGMT/UserFullGiveawaysHistoryUI', methods=['GET'])
def user_full_giveaways_history_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.generate_user_full_giveaways_history_ui(groups)
    return response


@app.route('/SGMT/UserFullGiveawaysHistory', methods=['GET'])
def user_full_giveaways_history():
    group_webpage = request.args.get('group_webpage')
    user = request.args.get('user')
    start_date = request.args.get('start_date')

    if not group_webpage or not user:
        return 'UserFullGiveawaysHistory  - For a single user, show a list of all giveaways he either created or participated in.<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               'user - A SteamGift user name <BR>' \
               '<B>Optional Params:</B> <BR>' \
               'start_date=YYYY-MM-DD - The date from which to fetch the data <BR>' \
               '<BR>'\
               '<A HREF="/SGMT/UserFullGiveawaysHistory?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&start_date=2017-12-01&user=Mdk25">Request Example</A>'

    created_giveaways, entered_giveaways, games = SGMTBusinessLogic.get_user_all_giveways(group_webpage, user, start_date)
    response = HtmlResponseGenerationService.generate_user_full_history_response(created_giveaways, entered_giveaways, games, user)
    return response


@app.route('/SGMT/GroupUsersSummaryUI', methods=['GET'])
def group_users_summary_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.generate_group_users_summary_ui(groups)
    return response


@app.route('/SGMT/GroupUsersSummary', methods=['GET'])
def group_users_summary():
    group_webpage = request.args.get('group_webpage')
    start_date = request.args.get('start_date')

    if not group_webpage:
        return 'GroupUsersSummary  - For a given group, return summary of all giveaways created, entered and won by members.<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               '<B>Optional Params:</B> <BR>' \
               'start_date=YYYY-MM-DD - The date starting from which to fetch the data <BR>' \
               '<BR>'\
               '<A HREF="/SGMT/GroupUsersSummary?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&start_date=2017-12-01">Request Example</A>'

    total_group_data, users_data = SGMTBusinessLogic.get_group_summary(group_webpage, start_date)
    response = HtmlResponseGenerationService.generate_group_users_summary_response(group_webpage, total_group_data, users_data, start_date)
    return response


@app.route('/SGMT/UserCheckRulesUI', methods=['GET'])
def user_check_rules_ui():
    response = HtmlUIGenerationService.generate_user_check_rules_ui()
    return response


@app.route('/SGMT/UserCheckRules', methods=['GET'])
def user_check_rules():
    users = request.args.get('users')
    check_nonactivated = request.args.get('check_nonactivated')
    check_multiple_wins = request.args.get('check_multiple_wins')
    check_real_cv_value = request.args.get('check_real_cv_value')
    check_steamgifts_ratio = request.args.get('check_steamgifts_ratio')
    check_level = request.args.get('check_level')
    level = get_optional_int_param('level')
    check_steamrep = request.args.get('check_steamrep')

    if not users:
        return 'UserCheckRules - Check if a user complies to group rules.<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'users - SteamGifts users to check<BR>' \
               '<B>Optional Params:</B> <BR>' \
               'check_nonactivated=True/False - Check user doesn\'t have non activated games<BR>' \
               'check_multiple_wins=True/False - Check user doesn\'t have multiple wins<BR>' \
               'check_real_cv_value=True/False - Check user has positive real CV ratio<BR>' \
               'check_steamgifts_ratio=True/False - Check user has positive SteamGifts global ratio<BR>' \
               'check_steamrep=True/Faalse - Check user has no SteamRep bans and his profile is public<BR>' \
               'check_level=True/False - Check user is above certain level<BR>' \
               'level=# - Check user is above certain level<BR>' \
               '<BR>'\
               '<A HREF="/SGMT/UserCheckRules?user=Mdk25&check_nonactivated=True&check_multiple_wins=True&check_real_cv_value=True&check_steamgifts_ratio=True&check_steamrep=True&check_level=True&level=1">Request Example</A>'

    response = u''
    users_list = users.split(',')
    for user in users_list:
        nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, is_level, steamrep = SGMTBusinessLogic.user_check_rules(user, check_nonactivated, check_multiple_wins, check_real_cv_value, check_steamgifts_ratio, check_level, level, check_steamrep)
        response += HtmlResponseGenerationService.generate_user_check_rules_response(user, nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, is_level, steamrep)
    return response


@app.route('/SGMT/PopularGiveawaysUI', methods=['GET'])
def popular_giveaways_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.generate_popular_giveaways_ui(groups)
    return response


@app.route('/SGMT/PopularGiveaways', methods=['GET'])
def popular_giveaways():
    group_webpage = request.args.get('group_webpage')
    check_param = request.args.get('check_param')
    year_month = request.args.get('year_month')
    year = request.args.get('year')
    month = request.args.get('month')
    if not year_month and year and month:
        year_month = year + '-' + month
    group_only_users = request.args.get('group_only_users')
    num_of_days = get_optional_int_param('num_of_days')

    if not group_webpage or not year_month or (check_param != 'TotalEntries' and check_param != 'EntriesOnFinish' and check_param != 'EntriesWithinXDays'):
        return 'PopularGiveaways - Get most popular giveaways in a group in a given month.<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               'check_param=TotalEntries/EntriesOnFinish/EntriesWithinXDays - Parameter according to which to measure popularity<BR>' \
               'year_month=YYYY-MM - The Year/Month for which to perform the check <BR>' \
               '<B>Optional Params:</B> <BR>' \
               'group_only_users=True/False - Count only entries from users in the group<BR>' \
               'num_of_days - In case of EntriesWithinXDays. the number of days <BR>' \
               '<BR>'\
               '<A HREF="/SGMT/PopularGiveaways?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&check_param=TotalEntries&year_month=2018-04&group_only_users=True">Request Example</A>'

    popular_giveaways = SGMTBusinessLogic.get_popular_giveaways(group_webpage, check_param, year_month, group_only_users, num_of_days)
    response = HtmlResponseGenerationService.generate_popular_giveaways_response(popular_giveaways, year_month)
    return response


@app.route('/SGMT/CheckGameGiveawaysUI', methods=['GET'])
def check_game_giveaways_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.check_game_giveaways_ui(groups)
    return response


@app.route('/SGMT/CheckGameGiveaways', methods=['GET'])
def check_game_giveaways():
    group_webpage = request.args.get('group_webpage')
    game_name = request.args.get('game_name').strip()
    start_date = request.args.get('start_date')

    if not group_webpage:
        return 'CheckGameGiveaways  - Number of group entries every time a game was given away in the group.<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               'game_name - Full name of the game<BR>' \
               '<B>Optional Params:</B> <BR>' \
               'start_date=YYYY-MM-DD - The date starting from which to fetch the data <BR>' \
               '<BR>'\
               '<A HREF="/SGMT/CheckGameGiveaways?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&game_name=BATTLETECH">Request Example</A>'

    all_game_giveaways = SGMTBusinessLogic.get_game_giveaways(group_webpage, game_name, start_date)
    response = HtmlResponseGenerationService.generate_all_game_giveaways_response(game_name, all_game_giveaways)
    return response



@app.route('/SGMT/AddNewGroupUI', methods=['GET'])
def ulazy_add_group_ui():
    response = HtmlUIGenerationService.generate_lazy_add_group_ui()
    return response


@app.route('/SGMT/AddNewGroup', methods=['GET'])
def lazy_add_group():
    group_webpage = request.args.get('group_webpage')
    cookies = request.args.get('cookies')

    if not group_webpage:
        return 'AddNewGroup - Add new group to SteamGifts Group Management Tool (SGMT).<BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               '<BR>'\
               '<A HREF="/SGMT/AddNewGroup?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group">Request Example</A>'

    group_name = SGMTBusinessLogic.lazy_add_group(group_webpage, cookies)
    return 'Succesfully added group <A HREF="' + group_webpage + '">' + group_name.replace('<','&lt;') + '</A>.<BR> ' \
          ' Please allow up to 24 hours for the group to be processed.'


@app.route('/SGMT/GetAvailableGroups', methods=['GET'])
def get_groups():
    groups, empty_groups = SGMTBusinessLogic.get_groups()
    response = HtmlResponseGenerationService.generate_get_groups_response(empty_groups, groups)
    return response


# --- Internal Admin Commands ---

@app.route('/SGMT-Admin/', methods=['GET'])
def amdin_main_page():
    response = ''
    response += '<A HREF="/SGMT-Admin/UpdateGroupData?group_webpage=">UpdateGroupData</A> - Partial update, single group.<BR><BR>'
    response += '<A HREF="/SGMT-Admin/AddNewGroup?group_webpage=">AddNewGroup</A> - Reload from scratch, single group.<BR><BR>'
    response += '<A HREF="/SGMT-Admin/UpdateAllGroups">UpdateAllGroups</A> - Partial update, all groups. Reload from scratch, all users, all games.<BR><BR>'
    response += '<A HREF="/SGMT-Admin/GroupUsersCheckRules">GroupUsersCheckRules</A> - Check accordance to rules of an entire SG group.<BR><BR>'

    return response


@app.route('/SGMT-Admin/AddNewGroup', methods=['GET'])
def add_new_group():
    start_time = time.time()
    group_webpage = request.args.get('group_webpage')
    cookies = request.args.get('cookies')
    start_date = request.args.get('start_date')
    SGMTBusinessLogic.add_new_group(group_webpage, cookies, start_date)
    LogUtils.log_info('AddNewGroup ' + group_webpage + ' took ' + str(time.time() - start_time) +  ' seconds')
    return json.dumps({'success': True, 'timestamp':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200, {'ContentType': 'application/json'}


@app.route('/SGMT-Admin/UpdateGroupData', methods=['GET'])
def update_group_data():
    start_time = time.time()
    group_webpage = request.args.get('group_webpage')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    force_full_run = request.args.get('force_full_run')
    SGMTBusinessLogic.update_existing_group(group_webpage, start_date, end_date, force_full_run, update_games=True)
    LogUtils.log_info('UpdateGroupData ' + group_webpage + ' took ' + str(time.time() - start_time) +  ' seconds')
    return json.dumps({'success': True, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200, {'ContentType': 'application/json'}


@app.route('/SGMT-Admin/UpdateAllGroups', methods=['GET'])
def update_all_groups():
    start_time = time.time()
    LogUtils.log_info('UpdateAllGroups started to run')
    SGMTBusinessLogic.update_all_db_groups()
    LogUtils.log_info('UpdateAllGroups took ' + str(time.time() - start_time) +  ' seconds')
    return json.dumps({'success': True, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200, {'ContentType': 'application/json'}


@app.route('/SGMT-Admin/UpdateAllGames', methods=['GET'])
def update_all_games():
    start_time = time.time()
    LogUtils.log_info('UpdateAllGames started to run')
    SGMTBusinessLogic.update_all_db_games_data()
    LogUtils.log_info('UpdateAllGames took ' + str(time.time() - start_time) +  ' seconds')
    return json.dumps({'success': True, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200, {'ContentType': 'application/json'}


@app.route('/SGMT-Admin/UpdateAllUsers', methods=['GET'])
def update_all_users():
    start_time = time.time()
    LogUtils.log_info('UpdateAllUsers started to run')
    SGMTBusinessLogic.update_all_db_users_data()
    LogUtils.log_info('UpdateAllUsers took ' + str(time.time() - start_time) +  ' seconds')
    return json.dumps({'success': True, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200, {'ContentType': 'application/json'}


@app.route('/SGMT-Admin/UpdateBundledGames', methods=['GET'])
def update_bundled_games():
    start_time = time.time()
    LogUtils.log_info('UpdateBundledGames started to run')
    SGMTBusinessLogic.update_bundled_games_data()
    LogUtils.log_info('UpdateBundledGames took ' + str(time.time() - start_time) +  ' seconds')
    return json.dumps({'success': True, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200, {'ContentType': 'application/json'}



@app.route('/SGMT-Admin/GroupUsersCheckRules', methods=['GET'])
def group_users_check_rules():
    group_webpage = request.args.get('group_webpage')
    check_nonactivated = request.args.get('check_nonactivated')
    check_multiple_wins = request.args.get('check_multiple_wins')
    check_real_cv_value = request.args.get('check_real_cv_value')
    check_steamgifts_ratio = request.args.get('check_steamgifts_ratio')
    check_level = request.args.get('check_level')
    level = get_optional_int_param('level')
    check_steamrep = request.args.get('check_steamrep')

    if not group_webpage:
        return 'GroupUsersCheckRules - Check if a user complies to group rules.<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               '<B>Optional Params:</B> <BR>' \
               'check_nonactivated=True/False - Check user doesn\'t have non activated games<BR>' \
               'check_multiple_wins=True/False - Check user doesn\'t have multiple wins<BR>' \
               'check_real_cv_value=True/False - Check user has positive real CV ratio<BR>' \
               'check_steamgifts_ratio=True/False - Check user has positive SteamGifts global ratio<BR>' \
               'check_steamrep=True/Faalse - Check user has no SteamRep bans and his profile is public<BR>' \
               'check_level=True/False - Check user is above certain level<BR>' \
               'level=# - Check user is above certain level<BR>' \
               '<BR>'\
               '<A HREF="/SGMT/GroupUsersCheckRules?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&check_nonactivated=True&check_multiple_wins=True&check_real_cv_value=True&check_steamgifts_ratio=True&check_steamrep=True&check_level=True&level=1">Request Example</A>'

    response = u''
    group_users_rules = SGMTBusinessLogic.group_users_check_rules(group_webpage, check_nonactivated, check_multiple_wins, check_real_cv_value, check_steamgifts_ratio, check_level, level, check_steamrep)
    for user, rules in group_users_rules.items():
        user_response = HtmlResponseGenerationService.generate_user_check_rules_response(user, rules[0], rules[1], rules[2],rules[3], rules[4], rules[5])
        LogUtils.log_info(user_response)
        response += user_response
    return response


@app.route('/SGMT-Admin/Test', methods=['GET'])
def test():
    response = u''
    SGMTBusinessLogic.test()
    return response


@app.route('/SGMT/legal', methods=['GET'])
def warranty():
    return '<B>Warranty</B> - This program is distributed in the hope that it will be useful,<BR>' \
           'but WITHOUT ANY WARRANTY; without even the implied warranty of<BR>' \
           'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<BR>' \
           'GNU General Public License for more details.<BR><BR>' \
            '<B>Conditions</B> - This program is free software: you can redistribute it and/or modify<BR>' \
           'it under the terms of the GNU General Public License as published by<BR>' \
           'the Free Software Foundation, either version 3 of the License, or<BR>' \
           '(at your option) any later version.'


@app.route('/SGMT/servicecheck', methods=['GET'])
def service_check():
    return 'OK'


def get_optional_int_param(param_name):
    param_value = request.args.get(param_name)
    if param_value:
        return int(param_value)
    return 0


def get_optional_float_param(param_name):
    param_value = request.args.get(param_name)
    if param_value:
        return float(param_value)
    return 0.0




if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    app.run(debug=True)