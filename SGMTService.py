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
    min_game_value = 0.0
    min_steam_num_of_reviews = 0
    min_steam_score = 0
    min_game_value_param = request.args.get('min_game_value')
    if min_game_value_param:
        min_game_value = float(min_game_value_param)
    min_steam_num_of_reviews_param = request.args.get('min_steam_num_of_reviews')
    if min_steam_num_of_reviews_param:
        min_steam_num_of_reviews = int(min_steam_num_of_reviews_param)
    min_steam_score_param = request.args.get('min_steam_score')
    if min_steam_score_param:
        min_steam_score = int(min_steam_score_param)
    if not group_webpage or not year_month or not cookies:
        return 'Missing params: group_webpage and/or year_month and/or cookies<BR><BR>'\
               'Usage: /SGMT/CheckMonthly?group_webpage=[steamgifts group webpage]&cookies=[your steamgifts cookies]&year_month=[Year+Month: YYYY-MM] ' \
               '(Optional: &min_days=[Minimum number of days of a GA]&min_game_value=[Minimal game value (in $) allowed]&min_steam_num_of_reviews=[Minimal number of Steam reviews allowed for a game]&min_steam_score=[Minimal Steam score allowed for a game])<BR><BR>' \
               'Example: /SGMT/CheckMonthly?group_webpage=https://www.steamgifts.com/group/6HSPr/qgg-group&cookies="PHPSESSID=..."&year_month=2017-11&min_days=3&min_game_value=9.95&min_steam_num_of_reviews=100&min_steam_score=80'

    response = SGMTBusinessLogic.check_monthly(group_webpage, year_month, cookies, min_days, min_game_value, min_steam_num_of_reviews, min_steam_score)
    return response.replace('\n','<BT>')



if __name__ == '__main__':
    app.run(debug=True)