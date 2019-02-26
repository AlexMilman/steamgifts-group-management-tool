# HTML response generation service of SGMT
# Copyright (C) 2017  Alex Milman
import calendar
from datetime import datetime

from BusinessLogic.ScrapingUtils import SteamGiftsConsts, SGToolsConsts, SteamConsts


def generate_invalid_giveaways_response(games, invalid_giveaways):
    if not invalid_giveaways:
        return u'<B>No Invalid Giveaways found !</B>'

    response = u'<B>Invalid Giveaways:</B>'
    for user, user_giveaways in invalid_giveaways.iteritems():
        response += u'<BR>User ' + generate_user_link(user) + ':<BR>'

        for giveaway in sorted(user_giveaways, key=lambda x: x.end_time, reverse=True):
            game_name = giveaway.game_name
            game_data = games[game_name]
            response += u'<A HREF="' + giveaway.link + u'">' + game_name + u'</A>'
            if game_data:
                response += u' (Steam Value: ' + str(game_data.value) + u', Steam Score: ' + str(game_data.steam_score) + u', Num Of Reviews: ' + str(game_data.num_of_reviews) + u')'
            response += u' Ends on: ' + giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S')
            response += u'<BR>'
    return response


def generate_user_full_history_response(created_giveaways, entered_giveaways, games, user):
    response = u'<BR>User ' + generate_user_link(user) + ':<BR>'
    total_value = 0
    total_score = 0.0
    total_num_of_reviews = 0.0
    missing_data = 0
    for giveaway in created_giveaways:
        game_data = games[giveaway.game_name]
        if game_data:
            total_value += game_data.value
            total_score += game_data.steam_score
            total_num_of_reviews += game_data.num_of_reviews
        if not game_data or (game_data.steam_score == -1 and game_data.num_of_reviews == -1):
            missing_data += 1
    response += u'<BR>User created ' + str(len(created_giveaways)) + u' giveaways '
    if len(created_giveaways) > 1:
        total = len(created_giveaways) - missing_data
        response += u'(Total value of given away games: ' + str(total_value)
        if total > 0:
            response += u' Average game score: ' + str(total_score / total) + u' Average Num of reviews: ' + str(total_num_of_reviews / total)
        response += ')'
    response += u'<BR>'
    for giveaway in sorted(created_giveaways, key=lambda x: x.end_time, reverse=True):
        game_name = giveaway.game_name
        game_data = games[game_name]
        response += u'<A HREF="' + giveaway.link + u'">' + game_name + u'</A>'
        if game_data:
            response += u' (Steam Value: ' + str(game_data.value) + u', Steam Score: ' + str(game_data.steam_score) + u', Num Of Reviews: ' + str(game_data.num_of_reviews) + u')'
        response += u' Ends on: ' + giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S')
        response += u'<BR>'
    won = 0
    for giveaway in entered_giveaways:
        if user in giveaway.entries.keys() and giveaway.entries[user].winner:
            won += 1
    response += u'<BR>User entered ' + str(len(entered_giveaways)) + u' giveaways:<BR>'
    if won > 0:
        response = response[:-4]
        response += u' (Won ' + str(won) + u', Winning percentage: ' + str(float(won) / len(entered_giveaways) * 100) + u'%)<BR>'
    for giveaway in sorted(entered_giveaways, key=lambda x: x.end_time, reverse=True):
        game_data = games[giveaway.game_name]
        response += u'<A HREF="' + giveaway.link + u'">' + giveaway.game_name + u'</A>'
        if game_data:
            response += u' (Steam Value: ' + str(game_data.value) + u', Steam Score: ' + str(game_data.steam_score) + u', Num Of Reviews: ' + str(game_data.num_of_reviews) + u')'
        response += u', Ends on: ' + giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S')
        if giveaway.entries[user].entry_time:
            response += u', Entry date: ' + giveaway.entries[user].entry_time.strftime('%Y-%m-%d %H:%M:%S')
        if user in giveaway.entries.keys() and giveaway.entries[user].winner:
            response += u' <B>(WINNER)</B>'
        response += u'<BR>'
    return response


def generate_group_users_summary_response(group_webpage, total_group_data, users_data, start_date):
    response = u'Summary for group ' + group_webpage + u':<BR><BR>'
    # Total Games Value, Average games value, Average Game Score, Average Game NumOfReviews, Average number of entered per game, Average number of created per user, Average number of entrered per user, Average number of won per user
    response += u'Total value of games given away in group: $' + float_to_str(total_group_data[0]) + u'<BR>'
    response += u'Average value of a game: $' + float_to_str(total_group_data[1]) + u'<BR>'
    response += u'Average steam score per game: ' + float_to_str(total_group_data[2]) + u'<BR>'
    response += u'Average number of steam reviews per game: ' + float_to_str(total_group_data[3]) + u'<BR>'
    response += u'Average number of group member entries per giveaway: ' + float_to_str(total_group_data[4]) + u'<BR><BR>'

    response += u'Average number of giveaways created by user: ' + float_to_str(total_group_data[5]) + u'<BR>'
    response += u'Average number of giveaways entered by user: ' + float_to_str(total_group_data[6]) + u'<BR>'
    response += u'Average number of giveaways won by user: ' + float_to_str(total_group_data[7]) + u'<BR>'
    response += u'<BR><BR>Summaries for all group users:<BR>'
    for user_name in sorted(users_data.keys(), key=lambda x: users_data[x][1], reverse=True):
        user_data = users_data[user_name]
        response += u'<BR>User <A HREF="' + generate_full_data_link(group_webpage, start_date, user_name) + u'">' + user_name + u'</A>:<BR>'
        # Number of created GAs, Total Value, Average Value, Average Score, Average NumOfReviews
        user_created = user_data[0]
        if user_created:
            response += u'Created: '
            response += u'Number of GAs: ' + float_to_str(user_created[0]) \
                        + u', Total GAs value: $' + float_to_str(user_created[1]) \
                        + u', Average GA value: $' + float_to_str(user_created[2]) \
                        + u', Average GA Steam game score: ' + float_to_str(user_created[3]) \
                        + u', Average GA Steam number of reviews: ' + float_to_str(user_created[4]) + u'<BR>'

        # Number of entered GAs, Percentage of unique, Total Value, Average Value, Average Score, Average Num Of Reviews
        user_entered = user_data[1]
        if user_entered:
            response += u'Entered: '
            response += u'Number of GAs: ' + float_to_str(user_entered[0]) \
                        + u', Group-only GAs: ' + float_to_str(user_entered[1]) + u'%' \
                        + u', Total GAs value: $' + float_to_str(user_entered[2]) \
                        + u', Average GA value: $' + float_to_str(user_entered[3]) \
                        + u', Average GA Steam game score: ' + float_to_str(user_entered[4]) \
                        + u', Average GA Steam number of reviews: ' + float_to_str(user_entered[5]) + u'<BR>'

        # Number of won GAs, Winning percentage, Total value, Average Value, Average Score, Average Num Of Reviews
        user_won = user_data[2]
        if user_won:
            response += u'Won: '
            response += u'Number of GAs: ' + float_to_str(user_won[0]) \
                        + u', Won vs total entered: ' + float_to_str(user_won[1]) + u'%' \
                        + u', Total GAs value: $' + float_to_str(user_won[2]) \
                        + u', Average GA value: $' + float_to_str(user_won[3]) \
                        + u', Average GA Steam game score: ' + float_to_str(user_won[4]) \
                        + u', Average GA Steam number of reviews: ' + float_to_str(user_won[5]) + u'<BR>'
    return response


def generate_full_data_link(group_webpage, start_date, user_name):
    return u'/SGMT/UserFullGiveawaysHistory?group_webpage=' + group_webpage + u'&user=' + user_name + u'&start_date=' + start_date


def generate_check_monthly_response(group_webpage, users, monthly_posters, monthly_unfinished, inactive_users, year_month):
    response = u'<style>\
                    th {\
                        text-align: left;\
                    }\
                </style>'
    response += u'<BR><B>' + get_month_year_str(year_month) + u'</B><BR>'

    response += u'<BR>Users with unfinished monthly GAs:<BR>'
    for user, giveaways in monthly_unfinished.iteritems():
        if user not in monthly_posters:
            response += u'User ' + generate_user_link(user) + u' giveaways: '
            if giveaways and len(giveaways) > 0:
                for giveaway in giveaways:
                    response += u'<A HREF="' + giveaway.link + u'">' + giveaway.game_name + u'</A>, '
                response = response[:-2]
                response += '<BR>'

    if inactive_users:
        response += u'<BR><BR>Users inactive this month (did not enter any GAs):<BR>'
        for user in inactive_users:
            response += generate_user_link(str(user)) + u'<BR>'

    response += u'<BR><BR>Users without monthly giveaways:<BR>'
    response += u'<TABLE style="width:25%">'
    for user, user_data in users.iteritems():
        if user not in monthly_posters and user not in monthly_unfinished.keys() and inactive_users and user not in inactive_users:
            response += u'<TR>'
            response += u'<TH>' + generate_user_link(str(user)) + u'</TH><TH>' + '<A HREF="' + generate_full_data_link(group_webpage, '', user) + u'">User full GAs list</A></TH><TH>' + generate_steam_user_link(user_data.steam_id) + u'</TH>'
            response += u'</TR>'
    response += u'</TABLE>'

    return response


def generate_check_user_first_giveaway_response(user_first_giveaway, succesfully_ended, user_no_giveaway, user_entered_giveaway, time_to_create_over):
    response = u''
    for user_name in user_first_giveaway.keys():
        for group_giveaway, game_data in user_first_giveaway[user_name]:
            response += u'User ' + generate_user_link(user_name) + ' ' \
                        u'first giveaway: <A HREF="' + group_giveaway.link + u'">' + group_giveaway.game_name + u'</A> ' \
                        u' (Steam Value: ' + str(game_data.value) + u', Steam Score: ' + str(game_data.steam_score) + u', Num Of Reviews: ' + str(game_data.num_of_reviews) + u')'
            if user_name in succesfully_ended and group_giveaway.link in succesfully_ended[user_name]:
                response += u'<B> - Finished succesfully !!!</B>'
            elif datetime.now() <= group_giveaway.end_time:
                response += u' - Ends on: ' + group_giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                response += u' - Ended'
            response += u'<BR>'
        
    response += u'<BR>'
    for user in user_no_giveaway:
        response += u'User ' + generate_user_link(user) + ' did not create a GA yet!<BR>'
    
    response += u'<BR>'
    for user in user_entered_giveaway:
        group_giveaways = user_entered_giveaway[user]
        for group_giveaway in sorted(group_giveaways, key=lambda x: x.entries[user].entry_time, reverse=True):
            response += u'User ' + generate_user_link(user) + ' ' \
                        u'entered giveaway before his first giveaway was over: <A HREF="' + group_giveaway.link + '">' + group_giveaway.game_name + u'</A> ' \
                        u'(Entry date: ' + group_giveaway.entries[user].entry_time.strftime('%Y-%m-%d %H:%M:%S') + u')<BR>'

    if time_to_create_over:        
        response += u'<BR>Time to create first GA ended.<BR>'

    return response


def generate_user_check_rules_response(user, nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, level, steamrep):
    response=u''
    response += u'<BR>User ' + user + u':<BR>'
    if nonactivated:
        response += u'Has non-activated games: ' + linkify(SGToolsConsts.SGTOOLS_CHECK_NONACTIVATED_LINK + user) + u'<BR>'
    
    if multiple_wins:
        response += u'Has multiple wins: ' + linkify(SGToolsConsts.SGTOOLS_CHECK_MULTIPLE_WINS_LINK + user) + u'<BR>'
        
    if real_cv_ratio:
        response += u'Won more than Sent (Real CV value).<BR>' \
                    u'Real CV Won: ' + linkify(SGToolsConsts.SGTOOLS_CHECK_WON_LINK + user) + u'<BR>' \
                    u'Real CV Sent: ' + linkify(SGToolsConsts.SGTOOLS_CHECK_SENT_LINK + user) + u'<BR>'

    if steamgifts_ratio is not None:
        response += u'Won more than sent in SteamGifts:<BR>' \
                    u'Won: ' + steamgifts_ratio[0] + '<BR>' \
                    u'Sent: ' + steamgifts_ratio[1] + u'<BR>'
        
    if level is not None:
        response += u'User level is less than ' + level + u'<BR>'
        
    if steamrep is not None:
        response += u'User is not public or banned: ' + linkify(steamrep) + u' ()<BR>'

    if not nonactivated and not multiple_wins and not real_cv_ratio and steamgifts_ratio is None and level is None and steamrep is None:
        response += u'User passed every test !!!'
    
    return response


def generate_popular_giveaways_response(popular_giveaways, year_month):
    response = u'<style>\
                    th {\
                        text-align: left;\
                    }\
                </style>'

    response += u'<BR><B>Most Popular GAs for ' + get_month_year_str(year_month) + u':</B><BR><BR>'
    response += u'<TABLE style="width:45%">'
    for giveaway_data, num_of_entries in sorted(popular_giveaways.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        response += u'<TR>'
        response += u'<TH><A HREF="' + giveaway_data.link + u'">' + giveaway_data.game_name + u' </A></TH><TH>By: ' + generate_user_link(giveaway_data.creator) + '</TH><TH>Entries: ' + str(num_of_entries) + u'</TH>'
        response += u'</TR>'
    response += u'</TABLE>'

    return response


def generate_all_game_giveaways_response(game_name, all_game_giveaways):
    response = u'<style>\
                    th {\
                        text-align: left;\
                    }\
                </style>'

    response += u'<BR><B>Full list of "' + game_name + u'" GAs:</B><BR><BR>'
    response += u'<TABLE style="width:75%">'
    response += u'<B><TH>Game Name</TH><TH>Gifter</TH><TH>Group Entries</TH><TH>Start Time</TH><TH>End Time</TH></B>'
    for giveaway_data, num_of_entries in sorted(all_game_giveaways.iteritems(), key=lambda (k,v): k.end_time , reverse=True):
        response += u'<TR>'
        response += u'<TH><A HREF="' + giveaway_data.link + u'">' + giveaway_data.game_name + u' </A></TH><TH>' + generate_user_link(giveaway_data.creator) + '</TH><TH>' + str(num_of_entries) + u'</TH><TH>' + str(giveaway_data.start_time) + u'</TH><TH>' + str(giveaway_data.end_time) + u'</TH>'
        response += u'</TR>'
    response += u'</TABLE>'

    return response


def get_month_year_str(year_month):
    split_date = year_month.split('-')
    year = split_date[0]
    month = calendar.month_name[int(split_date[1])]
    month_year_str = month + u' ' + year
    return month_year_str


def linkify(url):
    return u'<A HREF="' + url + '">' + url + '</A>'

def generate_user_link(user):
    return u'<A HREF="' + SteamGiftsConsts.get_user_link(user) + u'">' + user + u'</A>'


def generate_steam_user_link(steam_id):
    return '<A HREF=' + SteamConsts.STEAM_PROFILE_LINK + steam_id + '>Steam</A>'


def generate_get_groups_response(empty_groups, groups):
    response = u'<B>Available Groups:</B><BR>'
    for group_name in groups.keys():
        if group_name not in empty_groups.keys():
            response += u'<BR> - <A HREF="' + groups[group_name] + '">' + group_name.replace('<','&lt;') + u'</A><BR>'

    response += u'<BR><BR>'
    response += u'<B>Groups awaiting processing:</B><BR>'
    for group_name in empty_groups.keys():
        response += u'<BR> - <A HREF="' + empty_groups[group_name] + u'">' + group_name.replace('<','&lt;') + u'</A><BR>'
    return response


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


