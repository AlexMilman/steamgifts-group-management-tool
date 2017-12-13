#!flask/bin/python
import json

import time
from flask import Flask
from flask import request

from BusinessLogic import SGMTBusinessLogic

# API Service of SGMT
# Copyright (C) 2017  Alex Milman
from BusinessLogic.ScrapingUtils import SteamGiftsConsts

app = Flask(__name__)


@app.route('/SGMT/CheckMonthly', methods=['GET'])
def check_monthly():
    group_webpage = request.args.get('group_webpage')
    year_month = request.args.get('year_month')
    min_days = get_optional_int_param(request.args.get('min_days'))
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')
    alt_min_game_value = get_optional_float_param('alt_min_game_value')
    alt_min_steam_num_of_reviews = get_optional_int_param('alt_min_steam_num_of_reviews')
    alt_min_steam_score = get_optional_int_param('alt_min_steam_score')

    if not group_webpage or not year_month:
        return 'CheckMonthly - Returns a list of all users who didn\'t create a giveaway in a given month<BR>' \
               'Usage: /SGMT/CheckMonthly?group_webpage=[steamgifts group webpage]&year_month=[Year+Month: YYYY-MM] ' \
               '(Optional: &min_days=[Minimum number of days of a GA]&min_game_value=[Minimal game value (in $) allowed]&min_steam_num_of_reviews=[Minimal number of Steam reviews allowed for a game]&min_steam_score=[Minimal Steam score allowed for a game])<BR><BR>' \
               '&alt_min_game_value=[Alt. Minimal game value (in $) allowed]&alt_min_steam_num_of_reviews=[Alt. Minimal number of Steam reviews allowed for a game]&alt_min_steam_score=[Alt. Minimal Steam score allowed for a game])<BR><BR>' \
               'Example: /SGMT/CheckMonthly?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&year_month=2017-11&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80'

    response = SGMTBusinessLogic.check_monthly(group_webpage, year_month, min_days, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score)
    return response.replace('\n','<BR>')


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
    check_entered_giveaways = request.args.get('check_entered_giveaways')

    if not group_webpage or not users:
        return 'UserCheckFirstGiveaway  - Check if users comply with first giveaway rules:<BT>' \
               'Creates a giveaway unique to the group. Creates the giveaway within X days of entering the group. Creates the giveaway for a minimum of X days.' \
               'Usage: /SGMT/UserCheckFirstGiveaway?group_webpage=[steamgifts group webpage]&users=[steamgifts usernames seperated by comma] ' \
               '(Optional: &addition_date=[date from which the user entered the group: YYYY-MM-DD]&days_to_create_ga=[within how many days since entering the group should the GA be created]&min_ga_time=[min GA running time (in days)]' \
               '&min_game_value=[Minimal game value (in $) allowed]&min_steam_num_of_reviews=[Minimal number of Steam reviews allowed for a game]&min_steam_score=[Minimal Steam score allowed for a game])<BR><BR>' \
               '&alt_min_game_value=[Alt. Minimal game value (in $) allowed]&alt_min_steam_num_of_reviews=[Alt. Minimal number of Steam reviews allowed for a game]&alt_min_steam_score=[Alt. Minimal Steam score allowed for a game])&check_entered_giveaways=[Check if user entered any group GAs while his first GA is active]<BR><BR>' \
               'Example: /SGMT/UserCheckFirstGiveaway?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&users=User1,User2&addition_date=2017-12-01&days_to_create_ga=2&min_ga_time=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80&check_entered_giveaways=True'

    response = SGMTBusinessLogic.check_user_first_giveaway(group_webpage, users, addition_date, days_to_create_ga, min_ga_time, min_game_value, min_steam_num_of_reviews, min_steam_score, alt_min_game_value, alt_min_steam_num_of_reviews, alt_min_steam_score, check_entered_giveaways)
    return response.replace('\n','<BR>')

# TODO: Convert the 2 endpoints into: GetUserFullGroupInfo + Move all logic into BL
@app.route('/SGMT/AllUsersEnteredGiveaways', methods=['GET'])
def all_user_entered_giveaways():
    group_webpage = request.args.get('group_webpage')
    start_date = request.args.get('start_date')

    if not group_webpage:
        return 'AllUsersEnteredGiveaways  - For a given group, returns all group giveaways its\' users have entered since a given date.<BT>' \
               'Usage: /SGMT/AllUsersEnteredGiveaways?group_webpage=[steamgifts group webpage]&start_date=[date from which you want to check: YYYY-MM-DD] ' \
               'Example: /SGMT/AllUsersEnteredGiveaways?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&start_date=2017-12-01'

    users_to_giveaways = SGMTBusinessLogic.get_group_all_entered_giveaways(group_webpage, start_date)
    response = u''
    for user, giveaways_data in users_to_giveaways.items():
        response += u'<BR>User <A HREF="' + SteamGiftsConsts.get_user_link(user) + u'">' + user + u'</A> entered ' + str(len(giveaways_data)) + ' giveaways'
        won = count_won(giveaways_data)
        if won > 0:
            response += ' (won ' + str(won) + ') Winning percentage: ' + str(float(won) / len(giveaways_data) * 100) + '%'
        response += ':<BR>'
        for giveaway_data in giveaways_data:
            response += u'<A HREF="' + giveaway_data[0] + u'">' + giveaway_data[1].decode('utf-8') + u'</A>'
            if giveaway_data[2]:
                response += ' (WINNER)'
            response += '<BR>'
    return response


def count_won(giveaways_data):
    count = 0
    for data in giveaways_data:
        if data[2]:
            count += 1
    return count


@app.route('/SGMT/AllUsersCreatedGiveaways', methods=['GET'])
def all_user_created_giveaways():
    group_webpage = request.args.get('group_webpage')
    start_date = request.args.get('start_date')

    if not group_webpage:
        return 'AllUsersCreatedGiveaways  - For a given group, returns all group giveaways its\' users have created since a given date.<BT>' \
               'Usage: /SGMT/AllUsersCreatedGiveaways?group_webpage=[steamgifts group webpage]&start_date=[date from which you want to check: YYYY-MM-DD] ' \
               'Example: /SGMT/AllUsersCreatedGiveaways?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&start_date=2017-12-01'

    users_to_giveaways = SGMTBusinessLogic.get_group_all_created_giveaways(group_webpage, start_date)
    response = u''
    for user, giveaways_data in users_to_giveaways.items():
        total_value = 0
        total_score = 0.0
        total_num_of_reviews = 0.0
        missing_data = 0
        for giveaway_data in giveaways_data:
            total_value += giveaway_data[2].value
            total_score += giveaway_data[2].steam_score
            total_num_of_reviews += giveaway_data[2].num_of_reviews
            if giveaway_data[2].steam_score == 0 and giveaway_data[2].num_of_reviews == 0:
                missing_data += 1
        response += u'<BR>User <A HREF="' + SteamGiftsConsts.get_user_link(user) + u'">' + user + u'</A> created ' + str(len(giveaways_data)) + ' giveaways '
        if len(giveaways_data) > 1:
            total = len(giveaways_data) - missing_data
            response += u'(Total value of given away games: ' + str(total_value) + u' Average game score: ' + str(total_score / total) + u' Average Num of reviews: ' + str(total_num_of_reviews / total) + ')'
        response += u'<BR>'

        for giveaway_data in giveaways_data:
            response += u'<A HREF="' + giveaway_data[0] + u'">' + giveaway_data[1].decode('utf-8') + u'</A>'
            response += u' (Steam Value: ' + str(giveaway_data[2].value) + u', Steam Score: ' + str(giveaway_data[2].steam_score) + u', Num Of Reviews: ' + str(giveaway_data[2].num_of_reviews) + u')\n'
            response += u'<BR>'
    return response


@app.route('/SGMT/GroupUsersSummary', methods=['GET'])
def group_users_summary():
    group_webpage = request.args.get('group_webpage')
    start_date = request.args.get('start_date')

    if not group_webpage:
        return 'GroupUsersSummary  - For a given group, return summary of all giveaways created, entered and won by members.<BT>' \
               'Usage: /SGMT/GroupUsersSummary?group_webpage=[steamgifts group webpage]&start_date=[date from which you want to check: YYYY-MM-DD] ' \
               'Example: /SGMT/GroupUsersSummary?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&start_date=2017-12-01'

    total_group_data, users_data = SGMTBusinessLogic.get_group_summary(group_webpage, start_date)

    response = u'Summary for group ' + group_webpage + u':<BR><BR>'
    # Total Games Value, Average games value, Average Game Score, Average Game NumOfReviews
    response += u'Total value of games given away in group: $' + float_to_str(total_group_data[0]) + '<BR>'
    response += u'Average value of a game: $' + float_to_str(total_group_data[1]) + '<BR>'
    response += u'Average game steam score per game: ' + float_to_str(total_group_data[2]) + '<BR>'
    response += u'Average game number of steam reviews per game: ' + float_to_str(total_group_data[3]) + '<BR>'

    response += u'<BR>Summaries for all group users:<BR>'
    for user_name, user_data in users_data.items():
        response += u'<BR>User <A HREF="' + SteamGiftsConsts.get_user_link(user_name) + u'">' + user_name + u'</A>:<BR>'
        # Number of created GAs, Total Value, Average Value, Average Score, Average NumOfReviews
        user_created = user_data[0]
        if user_created:
            response += u'Created: '
            response += u'Number of GAs: ' + float_to_str(user_created[0]) \
                        + u', Total GAs value: $' + float_to_str(user_created[1]) \
                        + u', Average GA value: $' + float_to_str(user_created[2]) \
                        + u', Average GA Steam game score: ' + float_to_str(user_created[3]) + u'%' \
                        + u', Average GA Steam number of reviews: ' + float_to_str(user_created[4]) + u'<BR>'

        # Number of entered GAs, Percentage of unique, Total Value, Average Value, Average Score, Average Num Of Reviews
        user_entered = user_data[1]
        if user_entered:
            response += u'Entered: '
            response += u'Number of GAs: ' + float_to_str(user_entered[0]) \
                        + u', Group-only GAs: ' + float_to_str(user_entered[1]) + u'%' \
                        + u', Total GAs value: $' + float_to_str(user_entered[2]) \
                        + u', Average GA value: $' + float_to_str(user_entered[3]) \
                        + u', Average GA Steam game score: ' + float_to_str(user_entered[4]) + u'%' \
                        + u', Average GA Steam number of reviews: ' + float_to_str(user_entered[5]) + u'<BR>'

        # Number of won GAs, Winning percentage, Total value, Average Value, Average Score, Average Num Of Reviews
        user_won = user_data[2]
        if user_won:
            response += u'Won: '
            response += u'Number of GAs: ' + float_to_str(user_won[0]) \
                        + u', Won vs total entered: ' + float_to_str(user_won[1]) + u'%' \
                        + u', Total GAs value: $' + float_to_str(user_won[2]) \
                        + u', Average GA value: $' + float_to_str(user_won[3]) \
                        + u', Average GA Steam game score: ' + float_to_str(user_won[4]) + u'%' \
                        + u', Average GA Steam number of reviews: ' + float_to_str(user_won[5]) + u'<BR>'

    return response


def count_won(giveaways_data):
    count = 0
    for data in giveaways_data:
        if data[2]:
            count += 1
    return count


@app.route('/SGMT/UserCheckRules', methods=['GET'])
def user_check_rules():
    user = request.args.get('user')
    check_nonactivated = request.args.get('check_nonactivated')
    check_multiple_wins = request.args.get('check_multiple_wins')
    check_real_cv_value = request.args.get('check_real_cv_value')
    check_steamgifts_ratio = request.args.get('check_steamgifts_ratio')
    check_level = request.args.get('check_level')
    level = int(request.args.get('level'))
    check_steamrep = request.args.get('check_steamrep')

    if not user:
        return 'UserCheckRules - Check if a user complies to group rules.<BT>' \
               'Usage: /SGMT/UserCheckRules?&user=[steamgifts username]&[options]<BR>' \
                'Options:<BR>' \
                'check_nonactivated=True/False - Check user doesn\'t have non activated games<BR>'\
                'check_multiple_wins=True/False - Check user doesn\'t have multiple wins<BR>'\
                'check_real_cv_value=True/False - Check user has positive real CV ratio<BR>'\
                'check_steamgifts_ratio=True/False - Check user has positive SteamGifts global ratio<BR>'\
                'check_steamrep=True/Faalse - Check user has no SteamRep bans and his profile is public<BR>'\
                'check_level=True/Faalse - Check user is above certain level<BR>'\
                'level=# - Check user is above certain level<BR>'\
               'Example: /SGMT/UserCheckRules?user=Mdk25&check_nonactivated=True&check_multiple_wins=True&check_real_cv_value=True&check_steamgifts_ratio=True&check_steamrep=True&check_level=True&level=1'

    response_object = SGMTBusinessLogic.user_check_rules(user, check_nonactivated, check_multiple_wins, check_real_cv_value, check_steamgifts_ratio, check_level, level, check_steamrep)
    response = ''
    for user in response_object.keys():
        response += 'User ' + user + ';<BR>'
        for user_message in response_object[user]:
            response += user_message + '<BR>'
    return response.replace('\n','<BR>')


#TODO: Add CheckAllGiveawaysAccordingToRules


@app.route('/SGMT-Admin/AddNewGroup', methods=['GET'])
def add_new_group():
    start_time = time.time()
    group_webpage = request.args.get('group_webpage')
    cookies = request.args.get('cookies')
    SGMTBusinessLogic.add_new_group(group_webpage, cookies)
    print 'UpdateGroupData ' + group_webpage + ' took ' + str(time.time() - start_time) +  ' seconds'
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/SGMT-Admin/UpdateGroupData', methods=['GET'])
def update_group_data():
    start_time = time.time()
    group_webpage = request.args.get('group_webpage')
    cookies = request.args.get('cookies')
    SGMTBusinessLogic.update_existing_group(group_webpage, cookies)
    print 'UpdateGroupData ' + group_webpage + ' took ' + str(time.time() - start_time) +  ' seconds'
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


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


def float_to_str(float_value):
    float_str = str(float_value)
    if '.' in float_str:
        float_split = float_str.split('.')
        if float_split[1] == '0':
            return float_split[0]
        after_decimal_point = len(float_split[1])
        if after_decimal_point > 2:
            return float_str[:-after_decimal_point + 2]
    return float_str


if __name__ == '__main__':
    app.run(debug=True)