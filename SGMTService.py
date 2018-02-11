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
    response = '<B>Group Management</B><BR><BR>'
    response += '<A HREF="/SGMT/UserCheckRulesUI">UserCheckRules</A> - Check if a user complies to group rules.<BR><BR>'
    response += '<A HREF="/SGMT/CheckMonthlyUI">CheckMonthly</A> - Returns a list of all users who didn\'t create a giveaway in a given month.<BR><BR>'
    response += '<A HREF="/SGMT/CheckAllGiveawaysAccordingToRulesUI">CheckAllGiveawaysAccordingToRules</A> - Returns a list of games created not according to given rules.<BR><BR>'
    response += '<A HREF="/SGMT/UserCheckFirstGiveawayUI">UserCheckFirstGiveaway</A> - Check if users comply with first giveaway rules (according to defined rules).<BR><BR>'
    response += '<A HREF="/SGMT/GroupUsersSummaryUI">GroupUsersSummary</A> - For a given group, return summary of all giveaways created, entered and won by members.<BR><BR>'
    response += '<A HREF="/SGMT/UserFullGiveawaysHistoryUI">UserFullGiveawaysHistory</A> - For a single user, show a detailed list of all giveaways he either created or participated in (Game link, value, score, winners, etc.).<BR><BR>'
    response += '<BR><BR><BR>'
    response += '<B>Tool Management</B><BR><BR>'
    response += '<A HREF="/SGMT/GetAvailableGroups">GetAvailableGroups</A> - List all SteamGifts groups available in the tool at the moment.<BR><BR>'
    response += '<A HREF="/SGMT/AddNewGroup">AddNewGroup</A> - Add new SteamGifts group to be processed at the next available opportunity (tipically within 24 hours).<BR><BR>'

    return response


@app.route('/SGMT/CheckMonthlyUI', methods=['GET'])
def check_monthly_ui():
    groups = SGMTBusinessLogic.get_groups_with_users()
    response = HtmlUIGenerationService.generate_check_monthly_ui(groups)
    return response


#TODO: Add group-only-ga flag + UI
@app.route('/SGMT/CheckMonthly', methods=['GET'])
def check_monthly():
    group_webpage = request.args.get('group_webpage')
    year_month = request.args.get('year_month')
    year = request.args.get('year')
    month = request.args.get('month')
    if not year_month and year and month:
        year_month = year + '-' + month
    min_days = get_optional_int_param('min_days')
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')
    alt_min_game_value = get_optional_float_param('alt_min_game_value')
    alt_min_steam_num_of_reviews = get_optional_int_param('alt_min_steam_num_of_reviews')
    alt_min_steam_score = get_optional_int_param('alt_min_steam_score')
    alt2_min_game_value = get_optional_float_param('alt2_min_game_value')
    alt2_min_steam_num_of_reviews = get_optional_int_param('alt2_min_steam_num_of_reviews')
    alt2_min_steam_score = get_optional_int_param('alt2_min_steam_score')

    if not group_webpage or not year_month:
        return 'CheckMonthly - Returns a list of all users who didn\'t create a giveaway in a given month<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               'year_month=YYYY-MM Year+Month for which you want to check  <BR>' \
               '<B>Optional Params:</B> <BR>' \
               'min_days - Minimum number of days of a GA<BR>' \
               'min_game_value - Minimal game value (in $) allowed<BR>' \
               'min_steam_num_of_reviews - Minimal number of Steam reviews allowed for a game<BR>' \
               'min_steam_score - Minimal Steam score allowed for a game<BR>' \
               'alt_min_game_value - Alternative minimal game value (in $) allowed<BR>' \
               'alt_min_steam_num_of_reviews - Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt_min_steam_score - Alternative Minimal Steam score allowed for a game<BR>' \
               'alt2_min_game_value - 2nd Alternative minimal game value (in $) allowed<BR>' \
               'alt2_min_steam_num_of_reviews - 2nd Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt2_min_steam_score - 2nd Alternative Minimal Steam score allowed for a game<BR>' \
               '<BR>' \
               '<A HREF="/SGMT/CheckMonthly?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&year_month=2017-11&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80">Request Example</A>'

    users, monthly_posters, monthly_unfinished = SGMTBusinessLogic.check_monthly(group_webpage, year_month, min_days, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score, alt2_min_game_value, alt2_min_steam_num_of_reviews, alt2_min_steam_score)
    response = HtmlResponseGenerationService.generate_check_monthly_response(users, monthly_posters, monthly_unfinished)
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
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')
    alt_min_game_value = get_optional_float_param('alt_min_game_value')
    alt_min_steam_num_of_reviews = get_optional_int_param('alt_min_steam_num_of_reviews')
    alt_min_steam_score = get_optional_int_param('alt_min_steam_score')

    if not group_webpage:
        return 'CheckAllGiveawaysAccordingToRules - Returns a list of all giveaways which were created not according to the rules<BR><BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               '<B>Optional Params:</B> <BR>' \
               'start_date=YYYY-MM-DD Start date from which to check giveaways <BR>' \
               'min_days - Minimum number of days of a GA<BR>' \
               'min_game_value - Minimal game value (in $) allowed<BR>' \
               'min_steam_num_of_reviews - Minimal number of Steam reviews allowed for a game<BR>' \
               'min_steam_score - Minimal Steam score allowed for a game<BR>' \
               'alt_min_game_value - Alternative minimal game value (in $) allowed<BR>' \
               'alt_min_steam_num_of_reviews - Alternative minimal number of Steam reviews allowed for a game<BR>' \
               'alt_min_steam_score - Alternative Minimal Steam score allowed for a game<BR>' \
               '<BR>' \
               '<A HREF="/SGMT/CheckAllGiveawaysAccordingToRules?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&start_date=2017-11-01&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80">Request Example</A>'

    invalid_giveaways, games = SGMTBusinessLogic.check_giveaways_valid(group_webpage, start_date, min_days, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score)
    response = HtmlResponseGenerationService.generate_invalid_giveaways_response(games, invalid_giveaways)
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
               '<B>Optional Params:</B> <BR>' \
               'addition_date=YYYY-MM-DD - The date from which the user was added to the group <BR>' \
               'days_to_create_ga - Within how many days of entering the group should the first GA be created<BR>' \
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

    user_first_giveaway, user_no_giveaway, user_entered_giveaway, time_to_create_over = SGMTBusinessLogic.check_user_first_giveaway(group_webpage, users, addition_date, days_to_create_ga, min_ga_time, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score, alt2_min_game_value, alt2_min_steam_num_of_reviews, alt2_min_steam_score, check_entered_giveaways)
    response = HtmlResponseGenerationService.generate_check_user_first_giveaway_response(user_first_giveaway, user_no_giveaway, user_entered_giveaway, time_to_create_over)
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


@app.route('/SGMT/AddNewGroup', methods=['GET'])
def lazy_add_group():
    group_webpage = request.args.get('group_webpage')
    cookies = request.args.get('cookies')

    if not group_webpage:
        return 'AddNewGroup - Check if a user complies to group rules.<BR>' \
               'There are 2 ways to process a SteamGifts group:<BR>' \
               '1. Basic: It can be processed by an "anonymous" user. Which means it will not have access to the list of giveaway entries, and can only see up to 3 winners in each giveaway<BR>' \
               '2. Recomended: It can be processed by a user who is a member of the SteamGifts group. Which means it will have full access to all available group data<BR>' \
               'In order to benefit from the full abilities of the SGMT tool, it is recommended you provide the cookies of a registered group user, when adding your group.' \
               'Your cookies can be seen under "Cookies" section of the <A HREF="https://www.mkyong.com/computer-tips/how-to-view-http-headers-in-google-chrome/">HTTP request</A> while browing SteamGifts<BR>' \
               'Without cookies, the following commands will only give partial results: UserCheckFirstGiveaway, UserFullGiveawaysHistory, GroupUsersSummary<BR>' \
               '<B>Params:</B><BR> ' \
               'group_webpage - SteamGifts group webpage<BR>' \
               '<B>Optional Params:</B> <BR>' \
               'cookies - Your SteamGifts cookies<BR>' \
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
    response += '<A HREF="/SGMT/UpdateGroupData?group_webpage=">UpdateGroupData</A> - Partial update, single group.<BR><BR>'
    response += '<A HREF="/SGMT/AddNewGroup?group_webpage=">AddNewGroup</A> - Reload from scratch, single group.<BR><BR>'
    response += '<A HREF="/SGMT/UpdateAllGroups">UpdateAllGroups</A> - Partial update, all groups. Reload from scratch, all users, all games.<BR><BR>'
    response += '<A HREF="/SGMT/GroupUsersCheckRules">GroupUsersCheckRules</A> - Check accordance to rules of an entire SG group.<BR><BR>'

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
    SGMTBusinessLogic.update_existing_group(group_webpage)
    LogUtils.log_info('UpdateGroupData ' + group_webpage + ' took ' + str(time.time() - start_time) +  ' seconds')
    return json.dumps({'success': True, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), 200, {'ContentType': 'application/json'}


@app.route('/SGMT-Admin/UpdateAllGroups', methods=['GET'])
def update_all_groups():
    start_time = time.time()
    SGMTBusinessLogic.update_all_db_users_data()
    SGMTBusinessLogic.update_all_db_games_data()
    SGMTBusinessLogic.update_all_db_groups()
    LogUtils.log_info('UpdateAllGroups took ' + str(time.time() - start_time) +  ' seconds')
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


@app.route('/SGMT/warranty', methods=['GET'])
def warranty():
    return 'This program is distributed in the hope that it will be useful,<BR>' \
           'but WITHOUT ANY WARRANTY; without even the implied warranty of<BR>' \
           'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<BR>' \
           'GNU General Public License for more details.'


@app.route('/SGMT/conditions', methods=['GET'])
def conditions():
    return 'This program is free software: you can redistribute it and/or modify<BR>' \
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