# HTML response generation service of SGMT
# Copyright (C) 2017  Alex Milman

def get_check_monthly_ui(groups):
    response = get_header('CheckMonthly')
    response += 'Group:&nbsp; &nbsp;<select name="group_webpage">'
    for group_name, group_webpage in groups.items():
        response += '<option value="' + group_webpage + '">' + group_name.replace('<','&lt;') + '</option>'
    response += '</select><BR><BR>'

    response += 'Year:&nbsp; &nbsp;<select name="year">'
    response += '<option value="2017">2017</option>'
    response += '<option value="2018">2018</option>'
    response += '</select>&nbsp; &nbsp;'

    response += 'Month:&nbsp; &nbsp;<select name="month">'
    for month in xrange(1, 13, 1):
        response += '<option value="' + str(month) + '">' + str(month) + '</option>'
    response += '</select><BR><BR>'

    response += '<BR><B>Optional:</B><BR><BR>'
    response += 'Minimum number of days of a GA: <input type="text" name="min_days" size=2><BR><BR>'
    response += 'Minimal game value (in $) allowed: <input type="text" name="min_game_value" size=3><BR><BR>'
    response += 'Minimal number of Steam reviews allowed for a game: <input type="text" name="min_steam_num_of_reviews" size=6><BR><BR>'
    response += 'Minimal Steam score allowed for a game: <input type="text" name="min_steam_score" size=3><BR><BR>'
    response += get_footer('Get Monthly GAs')
    return response


def get_user_check_rules_ui():
    response = get_header('UserCheckRules')
    response += 'User: <input type="text" name="users"><BR><BR>'
    response += '<input type="checkbox" name="check_nonactivated" value="true">Check user doesn\'t have non activated games<BR>'
    response += '<input type="checkbox" name="check_multiple_wins" value="true">Check user doesn\'t have multiple wins<BR>'
    response += '<input type="checkbox" name="check_real_cv_value" value="true">Check user has positive real CV ratio<BR>'
    response += '<input type="checkbox" name="check_steamgifts_ratio" value="true">Check user has positive SteamGifts global ratio<BR>'
    response += '<input type="checkbox" name="check_steamrep" value="true">Check user has no SteamRep bans and his profile is public<BR>'
    response += '<input type="checkbox" name="check_level" value="true">Check user is above certain level. Level:  <input type="text" name="level" size=1>  <BR>'
    response += get_footer('Check User')
    return response


def get_footer(button_text):
    response = '<BR>'
    response += '<input type="submit" value="' + button_text + '"></form>'
    response += '</body></html>'
    return response


def get_header(action):
    response = '<!DOCTYPE html><html><body>'
    response += '<form action="/SGMT/' + action + '">'
    return response