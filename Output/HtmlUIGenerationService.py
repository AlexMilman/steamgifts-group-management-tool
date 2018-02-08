# HTML response generation service of SGMT
# Copyright (C) 2017  Alex Milman

def get_check_monthly_ui(groups):
    response = '<!DOCTYPE html><html><body>'
    response += '<form action="/SGMT/CheckMonthly">'
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
    response += '<BR>'
    response += '<input type="submit" value="Get Monthly GAs"></form>'
    response += '</body></html>'
    return response