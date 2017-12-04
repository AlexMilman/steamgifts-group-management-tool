#!flask/bin/python
from flask import Flask
from flask import request

from BusinessLogic import SGMTBusinessLogic

# API Service of SGMT
# Copyright (C) 2017  Alex Milman

app = Flask(__name__)


@app.route('/SGMT/CheckMonthly', methods=['GET'])
def index():
    group_webpage = request.args.get('group_webpage')
    year_month = request.args.get('year_month')
    cookies = request.args.get('cookies')
    min_days = request.args.get('min_days')
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')

    if not group_webpage or not year_month or not cookies:
        return 'Missing params: group_webpage and/or year_month and/or cookies<BR><BR>'\
               'Usage: /SGMT/CheckMonthly?group_webpage=[steamgifts group webpage]&cookies=[your steamgifts cookies]&year_month=[Year+Month: YYYY-MM] ' \
               '(Optional: &min_days=[Minimum number of days of a GA]&min_game_value=[Minimal game value (in $) allowed]&min_steam_num_of_reviews=[Minimal number of Steam reviews allowed for a game]&min_steam_score=[Minimal Steam score allowed for a game])<BR><BR>' \
               'Example: /SGMT/CheckMonthly?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&cookies="PHPSESSID=..."&year_month=2017-11&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80'

    response = SGMTBusinessLogic.check_monthly(group_webpage, year_month, cookies, min_days, min_game_value, min_steam_num_of_reviews, min_steam_score)
    return response.replace('\n','<BT>')


@app.route('/SGMT/UserCheckFirstGiveaway', methods=['GET'])
def index():
    group_webpage = request.args.get('group_webpage')
    user = request.args.get('user')
    cookies = request.args.get('cookies')
    addition_date = request.args.get('addition_date')
    days_to_create_ga = get_optional_int_param('days_to_create_ga')
    min_ga_time = get_optional_int_param('min_ga_time')
    min_game_value = get_optional_float_param('min_game_value')
    min_steam_num_of_reviews = get_optional_int_param('min_steam_num_of_reviews')
    min_steam_score = get_optional_int_param('min_steam_score')

    if not group_webpage or not user or not cookies:
        return 'Missing params: group_webpage and/or user and/or cookies<BR><BR>'\
               'UserCheckFirstGiveaway  - Check if a user complies with first giveaway rules:<BT>' \
               'Creates a giveaway unique to the group. Creates the giveaway within X days of entering the group. Creates the giveaway for a minimum of X days.' \
               'Usage: /SGMT/UserCheckFirstGiveaway?group_webpage=[steamgifts group webpage]&user=[steamgifts username]&cookies=[your steamgifts cookies] ' \
               '(Optional: &addition_date=[date from which the user entered the group: YYYY-MM-DD]&days_to_create_ga=[within how many days since entering the group should the GA be created]&min_ga_time=[min GA running time (in days)]' \
               '&min_days=[Minimum number of days of a GA]&min_game_value=[Minimal game value (in $) allowed]&min_steam_num_of_reviews=[Minimal number of Steam reviews allowed for a game]&min_steam_score=[Minimal Steam score allowed for a game])<BR><BR>' \
               'Example: /SGMT/UserCheckFirstGiveaway?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&user=Mdk25&cookies="PHPSESSID=..."&addition_date=2017-12-01&days_to_create_ga=2&min_ga_time=3&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80'

    response = SGMTBusinessLogic.check_user_first_giveaway(group_webpage, user, cookies, addition_date, days_to_create_ga, min_ga_time, min_game_value, min_steam_num_of_reviews, min_steam_score)
    return response.replace('\n','<BT>')





@app.route('/SGMT/warranty', methods=['GET'])
def index():
    return 'This program is distributed in the hope that it will be useful,<BR>' \
           'but WITHOUT ANY WARRANTY; without even the implied warranty of<BR>' \
           'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<BR>' \
           'GNU General Public License for more details.'


@app.route('/SGMT/conditions', methods=['GET'])
def index():
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


if __name__ == '__main__':
    app.run(debug=True)