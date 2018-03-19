import ConfigParser
import sys

import datetime

from dateutil.relativedelta import relativedelta

from BusinessLogic.ScrapingUtils import SteamGiftsScrapingUtils, SGToolsScrapingUtils, SteamRepScrapingUtils, \
    SteamScrapingUtils, SteamGiftsConsts, SteamRepConsts, SteamConsts, SteamDBScrapingUtils
from BusinessLogic.Utils import LogUtils
from Data.GameData import GameData
from Data.Group import Group
from Data.GroupUser import GroupUser
from Database import MySqlConnector

# Internal business logic of different SGMT commands
# Copyright (C) 2017  Alex Milman

config = ConfigParser.ConfigParser()
config.read('application.config')
common_cookies = config.get('Web', 'Cookies')


def missing_after_n_giveaway(group_webpage, n, steam_thread):
    group = MySqlConnector.load_group(group_webpage)
    if not group:
        return None
    group_giveaways = group.group_giveaways
    group_users = group.group_users
    after_n_giveaways = SteamScrapingUtils.verify_after_n_giveaways(steam_thread, group_giveaways, group_users.keys())
    wins = get_user_wins(group)
    discrepancies = findDiscrepancies(n, wins, after_n_giveaways)
    return discrepancies


def get_user_wins(group_data):
    user_wins=dict()
    for giveaway in group_data.group_giveaways.values():
        for entry in giveaway.entries.values():
            user_name = entry.user_name
            if entry.winner and user_name in group_data.group_users.keys():
                if user_name not in user_wins:
                    user_wins[user_name] = set()
                user_wins[user_name].add(giveaway.link)
    return user_wins


def findDiscrepancies(N, wins, after_n_giveaways):
    discrepancies = dict()
    for user, won in wins.iteritems():
        after_n_user_giveaways = 0
        if user in after_n_giveaways:
            after_n_user_giveaways = len(after_n_giveaways[user])
        if (after_n_user_giveaways + 1) * N <= len(won):
            discrepancies[user] = 'won ' + str(len(won)) + ' times, but did after-' + str(N) + ' GAs only ' + str(after_n_user_giveaways) + ' times'
    return discrepancies


def get_all_after_n_giveaways_per_user(group_webpage, n, steam_thread):
    group = MySqlConnector.load_group(group_webpage)
    if not group:
        return None
    after_n_giveaways = SteamScrapingUtils.verify_after_n_giveaways(steam_thread, group.group_giveaways, group.group_users.keys())
    return after_n_giveaways


def get_all_user_giveaways(group_webpage):
    group = MySqlConnector.load_group(group_webpage)
    if not group:
        return None
    giveaways_per_user=dict()
    for giveaway in group.group_giveaways.values():
        poster = giveaway.creator
        if poster in group.group_users.keys():
            if poster not in giveaways_per_user:
                giveaways_per_user[poster] = set()
            giveaways_per_user[poster].add(giveaway.link)

    return giveaways_per_user


def get_all_user_wins(group_webpage):
    group = MySqlConnector.load_group(group_webpage)
    if not group:
        return None
    wins = get_user_wins(group)
    return wins


def get_stemagifts_to_steam_user_translation(group_webpage):
    group = MySqlConnector.load_group(group_webpage)
    if not group:
        return None
    steam_id_to_user = SteamScrapingUtils.get_steam_id_to_user_dict(group.group_users.values())
    return steam_id_to_user


def get_all_giveaways_in_group(group_webpage):
    group = MySqlConnector.load_group(group_webpage, load_users_data=False)
    if not group:
        return None
    return group.group_giveaways.values()


def get_all_users_in_group(group_webpage):
    group = MySqlConnector.load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    return group.group_users.keys()


def check_monthly(group_webpage, year_month, min_days=0, min_entries=1, min_value=0.0, min_num_of_reviews=0, min_score=0,
                  alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0,
                  alt2_min_value=0.0, alt2_min_num_of_reviews=0, alt2_min_score=0):
    split_date = year_month.split('-')
    year = int(split_date[0])
    month = int(split_date[1])
    month_start = year_month + '-01'
    if month == 12:
        month_end = str(year + 1) + '-01-01'
    else:
        month_end = str(year) + '-' + str(month + 1) + '-01'
    group = MySqlConnector.load_group(group_webpage, limit_by_time=True, ends_after_str=month_start, ends_before_str=month_end)
    if not group:
        return None
    users = group.group_users.keys()
    monthly_posters = set()
    monthly_unfinished = dict()
    for group_giveaway in group.group_giveaways.values():
        end_month = group_giveaway.end_time.month
        start_month = group_giveaway.start_time.month
        # If GA started in previous month, mark it as started on the 1th of the month
        if start_month == month - 1 and end_month == month:
            start_day = 1
            start_month = month
        else:
            start_day = group_giveaway.start_time.day
        end_day = group_giveaway.end_time.day
        creator = group_giveaway.creator
        if creator in users and len(group_giveaway.groups) == 1\
                and start_month == month and end_month == month\
                and end_day - start_day + 1 >= min_days:
            game_name = group_giveaway.game_name
            game_data = MySqlConnector.get_game_data(game_name)
            check_game_data(game_data, game_name)
            if game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score, alt2_min_value, alt2_min_num_of_reviews, alt2_min_score):
                if group_giveaway.has_winners() and len(group_giveaway.entries) > min_entries:
                    monthly_posters.add(creator)
                elif group_giveaway.end_time > datetime.datetime.now() or len(group_giveaway.entries) > 0:
                    if creator not in monthly_unfinished:
                        monthly_unfinished[creator] = set()
                    monthly_unfinished[creator].add(group_giveaway)

    return users, monthly_posters, monthly_unfinished


def check_giveaways_valid(group_webpage, start_date=None, min_days=0, min_entries=1, min_value=0.0, min_num_of_reviews=0, min_score=0,
                  alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0):
    group = MySqlConnector.load_group(group_webpage, limit_by_time=start_date, starts_after_str=start_date)
    if not group:
        return None
    users = group.group_users.keys()
    invalid_giveaways = dict()
    games = dict()
    for group_giveaway in group.group_giveaways.values():
        creator = group_giveaway.creator
        if creator in users:
            game_name = group_giveaway.game_name
            game_data = MySqlConnector.get_game_data(game_name)
            check_game_data(game_data, game_name)
            if not game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score)\
                    or (group_giveaway.end_time - group_giveaway.start_time).days < min_days\
                    or (datetime.datetime.now() > group_giveaway.end_time and len(group_giveaway.entries) < min_entries):
                if creator not in invalid_giveaways:
                    invalid_giveaways[creator] = set()
                invalid_giveaways[creator].add(group_giveaway)
                games[game_name] = game_data

    return invalid_giveaways, games


def get_users_with_negative_steamgifts_ratio(group_webpage):
    group = MySqlConnector.load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    users_with_negative_sg_ratio = set()
    for group_user in group.group_users.values():
        if group_user.global_won > group_user.global_sent:
            users_with_negative_sg_ratio.add(group_user.user_name)
    return users_with_negative_sg_ratio


def get_users_with_negative_group_ratio(group_webpage):
    group = MySqlConnector.load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    users_with_negative_ratio=[]
    for user in group.group_users.values():
        if user.group_won > user.group_sent:
            users_with_negative_ratio.append(user.user_name)
    return users_with_negative_ratio


def get_user_entered_giveaways(group_webpage, users, addition_date):
    group = MySqlConnector.load_group(group_webpage, load_users_data=False)
    if not group:
        return None
    response = ''
    users_list = users.split(',')
    for group_giveaway in group.group_giveaways.values():
        # Go over all giveaways not closed before "addition_date"
        if not addition_date or addition_date < group_giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S'):
            for user in users_list:
                if user in group_giveaway.entries:
                    response += 'User ' + user + ' entered giveaway: ' + group_giveaway.link + '\n'
    return response


def get_user_all_giveways(group_webpage, user, start_time):
    group = MySqlConnector.load_group(group_webpage, load_users_data=False, limit_by_time=start_time, starts_after_str=start_time)
    if not group:
        return None
    created_giveaways=[]
    entered_giveaways=[]
    games=dict()
    for group_giveaway in group.group_giveaways.values():
        if not start_time or start_time <= group_giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S'):
            game_name = group_giveaway.game_name
            if group_giveaway.creator == user:
                created_giveaways.append(group_giveaway)
                games[game_name] = MySqlConnector.get_game_data(game_name)
            elif user in group_giveaway.entries.keys():
                entered_giveaways.append(group_giveaway)
                games[game_name] = MySqlConnector.get_game_data(game_name)

    return created_giveaways, entered_giveaways, games


def get_group_summary(group_webpage, start_time):
    group = MySqlConnector.load_group(group_webpage, limit_by_time=start_time, starts_after_str=start_time)
    if not group:
        return None
    all_group_users = group.group_users.keys()
    users_created = dict()
    users_entered = dict()
    users_won = dict()
    group_games_count=0
    group_games_value=0.0
    group_games_without_data=0
    group_games_total_score=0.0
    group_games_total_num_of_reviews=0.0
    group_total_entered=0.0
    group_total_won=0.0
    for group_giveaway in group.group_giveaways.values():
        creator = group_giveaway.creator
        if creator not in all_group_users:
            continue
        # Go over all giveaways started after "addition_date"
        if not start_time or start_time <= group_giveaway.end_time.strftime('%Y-%m-%d %H:%M:%S'):
            group_games_count += 1
            game_data = MySqlConnector.get_game_data(group_giveaway.game_name)
            value = game_data.value
            group_games_value += value
            score = game_data.steam_score
            num_of_reviews = game_data.num_of_reviews
            game_data_available = score != -1 and num_of_reviews != -1
            if game_data_available:
                group_games_total_score += score
                group_games_total_num_of_reviews += num_of_reviews
            else:
                group_games_without_data += 1

            # Number of created GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
            if creator not in users_created:
                users_created[creator] = [0, 0, 0, 0, 0]
            users_created[creator][0] += 1
            users_created[creator][1] += value
            if game_data_available:
                users_created[creator][2] += 1
                users_created[creator][3] += score
                users_created[creator][4] += num_of_reviews

            for entry in group_giveaway.entries.values():
                user_name = entry.user_name
                if user_name not in all_group_users:
                    continue
                group_total_entered += 1
                # Number of entered GAs, Number of Unique GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
                if user_name not in users_entered:
                    users_entered[user_name] = [0, 0, 0, 0, 0, 0]
                users_entered[user_name][0] += 1
                if len(group_giveaway.groups) == 1:
                    users_entered[user_name][1] += 1
                users_entered[user_name][2] += value
                if game_data_available:
                    users_entered[user_name][3] += 1
                    users_entered[user_name][4] += score
                    users_entered[user_name][5] += num_of_reviews

                if entry.winner:
                    group_total_won += 1
                    # Number of won GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
                    if user_name not in users_won:
                        users_won[user_name] = [0, 0, 0, 0, 0]
                    users_won[user_name][0] += 1
                    users_won[user_name][1] += value
                    if game_data_available:
                        users_won[user_name][2] += 1
                        users_won[user_name][3] += score
                        users_won[user_name][4] += num_of_reviews


    group_average_game_value = group_games_value / group_games_count
    group_average_game_score = group_games_total_score / (group_games_count - group_games_without_data)
    group_average_game_num_of_reviews = group_games_total_num_of_reviews / (group_games_count - group_games_without_data)
    # Total Games Value, Average games value, Average Game Score, Average Game NumOfReviews, Average number of created per user, Average number of entrered per user, Average number of won per user
    total_group_data = (group_games_value, group_average_game_value, group_average_game_score, group_average_game_num_of_reviews, group_games_count / len(all_group_users), group_total_entered / len(all_group_users), group_total_won / len(all_group_users))

    # Number of created GAs, Total Value, Average Value, Average Score, Average NumOfReviews
    # Number of entered GAs, Percentage of unique, Average Value, Average Score, Average Num Of Reviews
    # If avialable: number of won GAs, Winning percentage, Average Value, Average Score, Average Num Of Reviews
    users_data = dict()
    for user in users_created.keys():
        if user not in users_data:
            users_data[user] = [(),(),()]
        # Number of created GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
        user_data = users_created[user]
        # Number of created GAs, Total Value, Average Value, Average Score, Average NumOfReviews
        if user_data[2] > 0:
            users_data[user][0] = (user_data[0], user_data[1], float(user_data[1]) / user_data[0], float(user_data[3]) / user_data[2], float(user_data[4]) / user_data[2])
        else:
            users_data[user][0] = (user_data[0], user_data[1], float(user_data[1]) / user_data[0], 0, 0)

    for user in users_entered.keys():
        if user not in users_data:
            users_data[user] = [(),(),()]
        # Number of entered GAs, Number of Shared GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
        user_data = users_entered[user]
        # Number of entered GAs, Percentage of unique, Total Value, Average Value, Average Score, Average Num Of Reviews
        if user_data[3] > 0:
            users_data[user][1] = (user_data[0], float(user_data[1]) / user_data[0] * 100, user_data[2], float(user_data[2]) / user_data[0], float(user_data[4]) / user_data[3], float(user_data[5]) / user_data[3])
        else:
            users_data[user][1] = (user_data[0], float(user_data[1]) / user_data[0] * 100, user_data[2], float(user_data[2]) / user_data[0], 0, 0)
        if user in users_won:
            # Number of won GAs, Total Value, Number of GAs with data, Total Score, Total NumOfReviews
            user_data = users_won[user]
            # Number of won GAs, Winning percentage, Total value, Average Value, Average Score, Average Num Of Reviews
            if user_data[2] > 0:
                users_data[user][2] = (user_data[0], float(user_data[0]) / users_data[user][1][0] * 100, user_data[1], float(user_data[1]) / user_data[0], float(user_data[3]) / user_data[2], float(user_data[4]) / user_data[2])
            else:
                users_data[user][2] = (user_data[0], float(user_data[0]) / users_data[user][1][0] * 100, user_data[1], float(user_data[1]) / user_data[0], 0, 0)

    return total_group_data, users_data


def check_user_first_giveaway(group_webpage, users, addition_date, days_to_create_ga=0, min_ga_time=0, min_entries=1,
                              min_value=0.0, min_num_of_reviews=0, min_score=0,
                              alt_min_value=0.0, alt_min_num_of_reviews=0, alt_min_score=0,
                              alt2_min_game_value=0, alt2_min_steam_num_of_reviews=0, alt2_min_steam_score=0,
                              check_entered_giveaways=False):
    group = MySqlConnector.load_group(group_webpage, load_users_data=False, limit_by_time=True, ends_after_str=addition_date)
    if not group:
        return None
    users_list = users.split(',')
    user_added_time = datetime.datetime.strptime(addition_date, '%Y-%m-%d')
    user_end_time=dict()
    user_first_giveaway=dict()
    succesfully_ended=dict()
    user_no_giveaway=set()
    for group_giveaway in group.group_giveaways.values():
        game_name = group_giveaway.game_name
        user_name = group_giveaway.creator
        if (user_name in users_list
            and
                len(group_giveaway.groups) == 1
            and
                (days_to_create_ga == 0 or group_giveaway.start_time <= user_added_time + datetime.timedelta(days=days_to_create_ga + 1))
            and
                (min_ga_time == 0
                or (min_ga_time > 0 and group_giveaway.end_time - group_giveaway.start_time >= datetime.timedelta(days=min_ga_time - 1)))):
            game_data = MySqlConnector.get_game_data(game_name)
            check_game_data(game_data, game_name)
            if game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score, alt2_min_game_value, alt2_min_steam_num_of_reviews, alt2_min_steam_score):
                if user_name not in user_end_time or group_giveaway.end_time < user_end_time[user_name]:
                    user_end_time[user_name] = group_giveaway.end_time
                if user_name not in user_first_giveaway:
                    user_first_giveaway[user_name] = set()
                user_first_giveaway[user_name].add((group_giveaway, game_data))

                if datetime.datetime.now() > group_giveaway.end_time and group_giveaway.has_winners() and len(group_giveaway.entries) > min_entries:
                    if user_name not in succesfully_ended:
                        succesfully_ended[user_name] = set()
                    succesfully_ended[user_name].add(group_giveaway.link)

    for user in users_list:
        if user not in user_end_time.keys():
            user_no_giveaway.add(user)

    partial_group_webpage = group_webpage.split(SteamGiftsConsts.STEAMGIFTS_LINK)[1]
    user_entered_giveaway=dict()
    for group_giveaway in group.group_giveaways.values():
        if check_entered_giveaways and user_added_time < group_giveaway.end_time:
            for user in users_list:
                if user in group_giveaway.entries \
                        and group_giveaway.entries[user].entry_time >= user_added_time \
                        and (user not in user_end_time or group_giveaway.entries[user].entry_time < user_end_time[user])\
                        and (len(group_giveaway.groups) == 1 or not SteamGiftsScrapingUtils.user_in_group(user, filter(lambda x: x != partial_group_webpage, group_giveaway.groups))):
                    #TODO: Add "Whitelist detected" warning
                    if user not in user_entered_giveaway:
                        user_entered_giveaway[user] = set()
                    user_entered_giveaway[user].add(group_giveaway)

    time_to_create_over = False
    if days_to_create_ga > 0 and datetime.date.today() > user_added_time.date() + datetime.timedelta(days=days_to_create_ga + 1):
        time_to_create_over = True

    return user_first_giveaway, succesfully_ended, user_no_giveaway, user_entered_giveaway, time_to_create_over


def check_game_data(game_data, game_name):
    if not game_data:
        LogUtils.log_error(u'Could not load game data: ' + game_name)
    elif game_data.value == -1 or game_data.num_of_reviews == -1 or game_data.steam_score == -1:
        LogUtils.log_error(u'Could not load full game data: ' + game_name)


def game_is_according_to_requirements(game_data, min_value, min_num_of_reviews, min_score, alt_min_value, alt_min_num_of_reviews, alt_min_score, alt2_min_value=0, alt2_min_num_of_reviews=0, alt2_min_score=0):
    if not game_data:
        return True
    if ((min_value == 0 or (game_data.value == 0 or game_data.value >= min_value))
         and (min_num_of_reviews == 0 or (game_data.num_of_reviews == -1 or min_num_of_reviews <= game_data.num_of_reviews))
         and (min_score == 0 or (game_data.steam_score == -1 or min_score <= game_data.steam_score))):
        return True
    if ((alt_min_value != 0 or alt_min_score != 0 or alt_min_num_of_reviews != 0)
        and (alt_min_value == 0 or (game_data.value == 0 or game_data.value >= alt_min_value))
        and (alt_min_num_of_reviews == 0 or (game_data.num_of_reviews == -1 or alt_min_num_of_reviews <= game_data.num_of_reviews))
        and (alt_min_score == 0 or (game_data.steam_score == -1 or alt_min_score <= game_data.steam_score))):
        return True
    if ((alt2_min_value != 0 or alt2_min_score != 0 or alt2_min_num_of_reviews != 0)
        and (alt2_min_value == 0 or (game_data.value == 0 or game_data.value >= alt2_min_value))
        and (alt2_min_num_of_reviews == 0 or (game_data.num_of_reviews == -1 or alt2_min_num_of_reviews <= game_data.num_of_reviews))
        and (alt2_min_score == 0 or (game_data.steam_score == -1 or alt2_min_score <= game_data.steam_score))):
        return True
    return False


def group_users_check_rules(group_webpage, check_nonactivated=False, check_multiple_wins=False, check_real_cv_ratio=False, check_steamgifts_ratio=False, check_level=False, min_level=0, check_steamrep=False):
    group = MySqlConnector.load_group(group_webpage, load_giveaway_data=False)
    if not group:
        return None
    result=dict()
    for user_name in group.group_users.keys():
        nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, level, steamrep = user_check_rules(user_name, check_nonactivated, check_multiple_wins, check_real_cv_ratio, check_steamgifts_ratio, check_level, min_level, check_steamrep)
        result[user_name] = (nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, level, steamrep)
    return result


def user_check_rules(user_name, check_nonactivated=False, check_multiple_wins=False, check_real_cv_ratio=False, check_steamgifts_ratio=False, check_level=False, min_level=0, check_steamrep=False):
    nonactivated=False
    multiple_wins=False
    real_cv_ratio=False
    steamgifts_ratio=None
    level=None
    steamrep=None
    group_user=None

    if check_nonactivated:
        LogUtils.log_info('Checking user ' + user_name + ' for non-activated games')
        if SGToolsScrapingUtils.check_nonactivated(user_name):
            nonactivated=True

    if check_multiple_wins:
        LogUtils.log_info('Checking user ' + user_name + ' for multiple wins')
        if SGToolsScrapingUtils.check_multiple_wins(user_name):
            multiple_wins=True

    if check_real_cv_ratio:
        LogUtils.log_info('Checking user ' + user_name + ' for Real CV ratio')
        if SGToolsScrapingUtils.check_real_cv_RATIO(user_name):
            real_cv_ratio=True

    if check_steamgifts_ratio:
        LogUtils.log_info('Checking user ' + user_name + ' for SteamGifts Global ratio')
        group_user = load_user(group_user, user_name)
        if group_user.global_won > group_user.global_sent:
            steamgifts_ratio = (str(group_user.global_won), str(group_user.global_sent))

    if check_level and min_level > 0:
        LogUtils.log_info('Checking user ' + user_name + ' for minimal level')
        group_user = load_user(group_user, user_name)
        if group_user.level < float(min_level):
            level=str(min_level)

    if check_steamrep:
        LogUtils.log_info('Checking user ' + user_name + ' in SteamRep')
        user_steam_id = SteamGiftsScrapingUtils.get_user_steam_id(user_name)
        if user_steam_id and not SteamRepScrapingUtils.check_user_not_public_or_banned(user_steam_id):
            steamrep=SteamRepConsts.get_steamrep_link(user_steam_id)

    return nonactivated, multiple_wins, real_cv_ratio, steamgifts_ratio, level, steamrep


def load_user(group_user, user_name):
    if not group_user:
        group_user = MySqlConnector.get_user_data(user_name)
    if not group_user:
        group_user = GroupUser(user_name)
        SteamGiftsScrapingUtils.update_user_additional_data(group_user)
        MySqlConnector.save_user(group_user)
    return group_user


def test():
    # WebUtils.get_html_page('https://www.steamgifts.com/giveaway/OCir9/plank-not-included/groups1')
    # group = add_new_group(group_webpage, '')
    # MySqlConnector.save_group(group_webpage, group)
    # group = MySqlConnector.MySqlConnector.load_group(group_webpage)

    # for group_user in group.group_users.values():
    #     print '\nUser: ' + group_user.user_name
    #     for message in user_check_rules(group_user.user_name, check_real_cv_value=True):
    #         print message
    #     if group_user.global_won > group_user.global_sent:
    #         print 'User ' + group_user.user_name + ' has negative global gifts ratio'
    game = GameData('Strategy & Tactics: Wargame...', 'http://store.steampowered.com/app/536740/', 2)

    try:
        SteamScrapingUtils.get_game_additional_data(game.game_name, game.game_link)
    except:
        SteamDBScrapingUtils.get_game_additional_data(game.game_name, game.game_link)
    pass


def lazy_add_group(group_webpage, cookies):
    if not cookies:
        cookies = ''
    group_name = SteamGiftsScrapingUtils.get_group_name(group_webpage, cookies)
    MySqlConnector.save_empty_group(group_name, group_webpage, cookies)
    return group_name


def add_new_group(group_webpage, cookies, start_date=None):
    group_name = SteamGiftsScrapingUtils.get_group_name(group_webpage)
    if not cookies:
        cookies = common_cookies
    games = update_group_data(group_webpage, cookies, Group(group_name=group_name, group_webpage=group_webpage, cookies=cookies), force_full_run=True, start_date=start_date)
    update_games_data(games)


def update_existing_group(group_webpage, start_date=None):
    group = MySqlConnector.load_group(group_webpage, fetch_not_started_giveaways=True)
    if not group:
        return None
    cookies = common_cookies
    if group.cookies:
        cookies = group.cookies
    games = update_group_data(group_webpage, cookies, group, start_date=start_date)
    update_games_data(games, update_value=True)


def get_groups():
    groups = MySqlConnector.get_all_groups()
    empty_groups = MySqlConnector.get_all_empty_groups()
    return groups, empty_groups


def get_groups_with_users():
    return MySqlConnector.get_all_groups_with_users()


def update_games_data(games, update_value=False):
    games_to_add = []
    games_to_update_value = []
    existing_games = MySqlConnector.get_existing_games_data(games.keys())
    for game in games.values():
        game_name = game.game_name.decode('utf-8')
        if game_name not in existing_games.keys():
            update_game_data(game)
            games_to_add.append(game)
        elif update_value and game.value != existing_games[game_name].value:
            games_to_update_value.append(game)

    if games_to_add:
        MySqlConnector.save_games(games_to_add)

    if games_to_update_value:
        MySqlConnector.update_existing_games(games_to_update_value)


def update_game_data(game):
    game_link = game.game_link
    game_name = game.game_name
    try:
        if game_link.startswith(SteamConsts.STEAM_GAME_LINK):
            try:
                steam_score, num_of_reviews = SteamScrapingUtils.get_game_additional_data(game_name, game_link)
            except:
                steam_score, num_of_reviews = SteamDBScrapingUtils.get_game_additional_data(game_name, game_link)
            game.steam_score = steam_score
            game.num_of_reviews = num_of_reviews
        elif game_link.startswith(SteamConsts.STEAM_PACKAGE_LINK):
            chosem_score = -1
            chosen_num_of_reviews = -1
            package_games = SteamScrapingUtils.get_games_from_package(game_name, game_link)
            i = 0
            for package_url in package_games:
                tmp_game_name = game_name + ' - package #' + str(i)
                try:
                    steam_score, num_of_reviews = SteamScrapingUtils.get_game_additional_data(tmp_game_name, package_url)
                except:
                    steam_score, num_of_reviews = SteamDBScrapingUtils.get_game_additional_data(tmp_game_name, package_url)
                if num_of_reviews > chosen_num_of_reviews:
                    chosem_score = steam_score
                    chosen_num_of_reviews = num_of_reviews
                i += 1
            game.steam_score = chosem_score
            game.num_of_reviews = chosen_num_of_reviews
        else:
            LogUtils.log_error('Don\'t know how to handle game: ' + game_name + ' at ' + game_link)
    except:
        LogUtils.log_error('Cannot add additional data for game: ' + game_name + ' ERROR: ' + str(sys.exc_info()[0]))


def update_group_data(group_webpage, cookies, group, force_full_run=False, start_date=None):
    group_users = SteamGiftsScrapingUtils.get_group_users(group_webpage)
    existing_users = MySqlConnector.check_existing_users(group_users.keys())
    for group_user in group_users.values():
        if group_user.user_name not in existing_users:
            try:
                SteamGiftsScrapingUtils.update_user_additional_data(group_user)
            except:
                LogUtils.log_error('Cannot add additional data for user: ' + group_user.user_name + ' ERROR: ' + str(sys.exc_info()[0]))

    group_giveaways, games = SteamGiftsScrapingUtils.get_group_giveaways(group_webpage, cookies, group.group_giveaways, force_full_run=force_full_run, start_date=start_date)
    remove_deleted_giveaways(cookies, group, group_giveaways)
    MySqlConnector.save_group(group_webpage, Group(group_users, group_giveaways, group_webpage=group_webpage, cookies=cookies, group_name=group.group_name), existing_users, group)

    return games


def remove_deleted_giveaways(cookies, group, group_giveaways):
    # If any existing GA is missing from newly parsed data - remove it from group giveaways.
    earliest_giveaway_end_time = sorted(filter(lambda x: x.end_time, group_giveaways.values()), key=lambda x: x.end_time)[0].end_time
    for giveaway in sorted(filter(lambda x: x.end_time, group.group_giveaways.values()), key=lambda x: x.end_time, reverse=True):
        if giveaway.end_time < earliest_giveaway_end_time:
            break
        if giveaway.link not in group_giveaways and not giveaway.has_winners() and SteamGiftsScrapingUtils.is_giveaway_deleted(giveaway.link, cookies):
            LogUtils.log_info('Removing deleted giveaway: ' + giveaway.link)
            group.group_giveaways.pop(giveaway.link, None)


def update_all_db_groups():
    #Load list of all groups from DB
    groups = MySqlConnector.get_all_groups()
    #For each group, run: update_group_data
    start_date = (datetime.datetime.now() - relativedelta(months=1)).replace(day=1).strftime('%Y-%m-%d')
    for group_url in groups.values():
        try:
            update_existing_group(group_url, start_date=start_date)
        except:
            LogUtils.log_error('Cannot update data for group: ' + group_url + ' ERROR: ' + str(sys.exc_info()[0]))


def update_all_db_users_data():
    #Load all DB users from DB
    users = MySqlConnector.get_all_users()
    #Go over list, check if any changed
    changed_users = []
    for user in users:
        new_user = GroupUser(user.user_name)
        SteamGiftsScrapingUtils.update_user_additional_data(new_user)
        if not user.equals(new_user):
            changed_users.append(new_user)
    #Save changed users to the DB
    if changed_users:
        MySqlConnector.update_existing_users(changed_users)


def update_all_db_games_data():
    #Load all games from DB
    games = MySqlConnector.get_all_games()
    #Go over all games, and update their data
    changed_games = []
    for game in games:
        new_game = GameData(game.game_name, game.game_link, game.value)
        update_game_data(new_game)
        if not game.equals(new_game):
            changed_games.append(new_game)
    #Save changed games to the DB
    if changed_games:
        MySqlConnector.update_existing_games(changed_games)