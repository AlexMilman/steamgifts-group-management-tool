# HTML response generation service of SGMT
# Copyright (C) 2017  Alex Milman

def generate_check_monthly_ui(groups):
    response = get_header('CheckMonthly - Returns a list of all users who didn\'t create a giveaway in a given month.','CheckMonthly')
    response += get_groups_dropdown(groups.values())

    response += 'Year:&nbsp; &nbsp;<select name="year">'
    response += '<option value="2017">2017</option>'
    response += '<option value="2018">2018</option>'
    response += '</select>&nbsp; &nbsp;'

    response += 'Month:&nbsp; &nbsp;<select name="month">'
    for month in xrange(1, 13, 1):
        response += '<option value="' + str(month) + '">' + str(month) + '</option>'
    response += '</select><BR><BR>'

    response += '<BR><B>Optional:</B><BR><BR>'
    response += get_min_days_with_game_stats()
    response += get_footer('Get Monthly GAs')
    return response


def generate_user_check_rules_ui():
    response = get_header('UserCheckRules - Check if a user complies to group rules.', 'UserCheckRules')
    response += 'User: <input type="text" name="users"><BR><BR>'
    response += '<input type="checkbox" name="check_nonactivated" value="true">Check user doesn\'t have non activated games<BR>'
    response += '<input type="checkbox" name="check_multiple_wins" value="true">Check user doesn\'t have multiple wins<BR>'
    response += '<input type="checkbox" name="check_real_cv_value" value="true">Check user has positive real CV ratio<BR>'
    response += '<input type="checkbox" name="check_steamgifts_ratio" value="true">Check user has positive SteamGifts global ratio<BR>'
    response += '<input type="checkbox" name="check_steamrep" value="true">Check user has no SteamRep bans and his profile is public<BR>'
    response += '<input type="checkbox" name="check_level" value="true">Check user is above certain level. Level:  <input type="text" name="level" size=1>  <BR>'
    response += get_footer('Check User')
    return response


def generate_check_all_giveaways_ui(groups):
    response = get_header('CheckAllGiveawaysAccordingToRules - Returns a list of games created not according to given rules.', 'CheckAllGiveawaysAccordingToRules')
    response += get_groups_dropdown(groups.values())

    response += get_optional_label()
    response += get_start_date()
    response += get_min_days_with_game_stats()
    response += get_footer('Check Giveaways')
    return response


def generate_user_check_first_giveaway_ui(groups):
    response = get_header('UserCheckFirstGiveaway - Check if users comply with first giveaway rules (according to defined rules).', 'UserCheckFirstGiveaway')
    response += get_groups_dropdown(groups.values())
    response += 'Users (comma-separated, e.g. Amy,Beck,Clark): <input type="text" name="users"><BR><BR>'
    response += 'The date from which the user was added to the group (e.g. 2017-12-31) : <input type="text" name="addition_date" size=10><BR><BR>'

    response += get_optional_label()
    response += 'Within how many days of entering the group should the first GA be created: <input type="text" name="days_to_create_ga" size=2><BR><BR>'
    response += 'Minimum number of days of a GA to run: <input type="text" name="min_ga_time" size=2><BR><BR>'
    response += get_game_stats()
    response += get_footer('Check First Giveaway')
    return response


def generate_group_users_summary_ui(groups):
    response = get_header('GroupUsersSummary  - For a given group, return summary of all giveaways created, entered and won by members.', 'GroupUsersSummary')
    response += get_groups_dropdown(groups.values())

    response += get_optional_label()
    response += get_start_date()
    response += get_footer('Get Users Summary')
    return response


def generate_user_full_giveaways_history_ui(groups):
    response = '<!DOCTYPE html><head><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script></head><body>'
    response += '<B>UserFullGiveawaysHistory - For a single user, show a detailed list of all giveaways he either created or participated in (Game link, value, score, winners, etc.).</B><BR><BR>'
    response += '<form action="/SGMT/UserFullGiveawaysHistory">'

    response += get_groups_dropdown(groups.values())
    response += 'User:&nbsp; &nbsp;<select id="user" name="user">'
    response += '</select><BR><BR>'

    response += get_optional_label()
    response += get_start_date()
    response += get_footer('Get User History')

    response += '<script>' + '\n'
    response += '$(\'#group_webpage\').on(\'change\', function() {' + '\n'
    response += ' $(\'#user\').html(\'\');' + '\n'
    response += ' switch($(\'#group_webpage\').val()) {' + '\n'
    for group in groups.values():
        response += '  case "' + group.group_webpage + '":' + '\n'
        for user in group.group_users:
          response += '   $(\'#user\').append(\'<option value="' + user + '">' + user + '</option>\');' + '\n'
        response += '   break;' + '\n'
    response += '  }});' + '\n'
    response += '</script>'

    return response


def get_min_days_with_game_stats():
    response = 'Minimum number of days of a GA: <input type="text" name="min_days" size=2><BR><BR>'
    response += get_game_stats()
    return response


def get_game_stats():
    response = 'Minimal game value (in $) allowed: <input type="text" name="min_game_value" size=3><BR><BR>'
    response += 'Minimal number of Steam reviews allowed for a game: <input type="text" name="min_steam_num_of_reviews" size=6><BR><BR>'
    response += 'Minimal Steam score allowed for a game: <input type="text" name="min_steam_score" size=3><BR><BR>'
    return response


def get_optional_label():
    return '<BR><B>Optional:</B><BR><BR>'


def get_start_date():
    return 'Start date (dash separated) from which to check data (e.g. 2017-12-31) : <input type="text" name="start_date" size=10><BR><BR>'


def get_groups_dropdown(groups):
    response = 'Group:&nbsp; &nbsp;<select id="group_webpage" name="group_webpage">'
    response += '<option/>'
    for group in groups:
        response += '<option value="' + group.group_webpage + '">' + group.group_name.replace('<', '&lt;') + '</option>'
    response += '</select><BR><BR>'
    return response


def get_footer(button_text):
    response = '<BR>'
    response += '<input type="submit" value="' + button_text + '"></form>'
    response += '</body></html>'
    return response


def get_header(title, action):
    response = '<!DOCTYPE html><html><body>'
    response += '<B>' + title + '</B><BR><BR>'
    response += '<form action="/SGMT/' + action + '">'
    return response

