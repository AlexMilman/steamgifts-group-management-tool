# MySql connector of SGMT
# Copyright (C) 2017  Alex Milman
import calendar
import json

import datetime
import pymysql
import ConfigParser

import time

from BusinessLogic.Utils import StringUtils, LogUtils
from Data.GameData import GameData
from Data.GiveawayEntry import GiveawayEntry
from Data.Group import Group
from Data.GroupGiveaway import GroupGiveaway
from Data.GroupUser import GroupUser

config = ConfigParser.ConfigParser()
config.read('application.config')
host = config.get('MySql', 'Host')
port = int(config.get('MySql', 'Port'))
user = config.get('MySql', 'User')
password = config.get('MySql', 'Password')
db_schema = config.get('MySql', 'DBSchema')


def save_group(group_website, group, users_to_ignore, existing_group_data=None):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    # Insert Giveaways
    giveaways_data = []
    group_giveaways_data = []
    for group_giveaway in group.group_giveaways.values():
        giveaway_id = StringUtils.get_hashed_id(group_giveaway.link)
        group_giveaways_data.append((giveaway_id, to_epoch(group_giveaway.start_time), to_epoch(group_giveaway.end_time)))

        entries_data = []
        for entry in group_giveaway.entries.values():
            entries_data.append((entry.user_name, to_epoch(entry.entry_time), entry.winner))
        giveaways_data.append((giveaway_id, group_giveaway.link, group_giveaway.creator, group_giveaway.game_name, json.dumps(entries_data), json.dumps(group_giveaway.groups)))

    if giveaways_data:
        cursor.executemany("INSERT INTO Giveaways (GiveawayID,LinkURL,Creator,GameName,Entries,Groups) VALUES (%s,%s,%s,%s,%s,%s)"\
                       + " ON DUPLICATE KEY UPDATE LinkURL=VALUES(LinkURL),Creator=VALUES(Creator),GameName=VALUES(GameName),Entries=VALUES(Entries),Groups=VALUES(Groups)", giveaways_data)

    # Merge with existing group data (in case of update/merge)
    if existing_group_data and existing_group_data.group_giveaways:
        for existing_giveaway_data in existing_group_data.group_giveaways.values():
            if existing_giveaway_data.link not in group.group_giveaways.keys():
                giveaway_id = StringUtils.get_hashed_id(existing_giveaway_data.link)
                group_giveaways_data.append((giveaway_id, to_epoch(existing_giveaway_data.start_time), to_epoch(existing_giveaway_data.end_time)))

    # Insert Users
    users_data = []
    group_users_data = []
    for group_user in group.group_users.values():
        group_users_data.append((group_user.user_name, group_user.group_won, group_user.group_sent))

        if group_user.user_name not in users_to_ignore:
            users_data.append((group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent, group_user.level))

    if users_data:
        cursor.executemany("INSERT INTO Users (UserName,SteamId,GlobalWon,GlobalSent,Level) VALUES (%s, %s, %s, %s, %s)"
                           " ON DUPLICATE KEY UPDATE UserName=VALUES(UserName),SteamId=VALUES(SteamId),GlobalWon=VALUES(GlobalWon),GlobalSent=VALUES(GlobalSent),Level=VALUES(Level)", users_data)

    # Insert Group
    group_id_str = "\"" + StringUtils.get_hashed_id(group_website) + "\""
    group_users_data_str = "\"" + json.dumps(group_users_data).replace('"', '\\"') + "\""
    group_giveaways_data_str = "\"" + json.dumps(group_giveaways_data).replace('"', '\\"') + "\""
    group_name_str = "\"" + to_str(group.group_name) + "\""
    group_webpage_str = "\"" + to_str(group.group_webpage) + "\""
    cookies_str = "\"" + to_str(group.cookies) + "\""
    cursor.execute("INSERT INTO Groups (GroupID,Users,Giveaways,Name,Webpage,Cookies) VALUES ("
                   + group_id_str + ","
                   + group_users_data_str + ","
                   + group_giveaways_data_str + ","
                   + group_name_str + ","
                   + group_webpage_str + ","
                   + cookies_str
                   + ") ON DUPLICATE KEY UPDATE Users=VALUES(Users),Giveaways=VALUES(Giveaways)")

    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    LogUtils.log_info('Save Group ' + group_website + ' took ' + str(time.time() - start_time) + ' seconds')


def load_group(group_website, load_users_data=True, load_giveaway_data=True, fetch_not_started_giveaways=False, limit_by_time=False, starts_after_str=None, ends_before_str=None, ends_after_str=None):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    # Load Group
    group_id = StringUtils.get_hashed_id(group_website)
    cursor.execute('SELECT Users,Giveaways,Cookies FROM Groups WHERE GroupID="' + group_id + '"')
    data = cursor.fetchone()
    group_users_data = json.loads(data[0])
    group_giveaways_data = json.loads(data[1])
    cookies = data[2]

    # Load Users Data
    group_users = dict()
    if load_users_data and group_users_data:
        for row in group_users_data:
            # (group_user.user_name, group_user.group_won, group_user.group_sent)
            user_name = row[0]
            group_users[user_name] = GroupUser(user_name, group_won=row[1], group_sent=row[2])

        cursor.execute('SELECT * FROM Users WHERE UserName in (' + parse_list(group_users.keys()) + ')')
        data = cursor.fetchall()
        for row in data:
            # (group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent, group_user.level)
            user_name = row[0]
            if user_name not in group_users:
                group_users[user_name] = GroupUser(user_name)
            group_users[user_name].steam_id=row[1]
            group_users[user_name].global_won=int(row[2])
            group_users[user_name].global_sent=int(row[3])
            group_users[user_name].level=int(row[4])

    # Load Giveaways Data
    group_giveaways = dict()
    giveaways_by_id=dict()
    if load_giveaway_data and group_giveaways_data:
        for row in group_giveaways_data:
            start_time_epoch = row[1]
            end_time_epoch = row[2]
            if not fetch_not_started_giveaways and not end_time_epoch:
                continue
            if limit_by_time and \
                    ((starts_after_str and datetime.datetime.utcfromtimestamp(start_time_epoch) < datetime.datetime.strptime(starts_after_str, '%Y-%m-%d'))
                     or (ends_before_str and datetime.datetime.utcfromtimestamp(end_time_epoch) > datetime.datetime.strptime(ends_before_str, "%Y-%m-%d"))
                     or (ends_after_str and datetime.datetime.utcfromtimestamp(end_time_epoch) < datetime.datetime.strptime(ends_after_str, "%Y-%m-%d"))):
                    continue
            # (giveaway_id, calendar.timegm(group_giveaway.start_time), calendar.timegm(group_giveaway.end_time))
            giveaway_id = row[0]
            giveaways_by_id[giveaway_id] = GroupGiveaway(None, start_time=from_epoch(start_time_epoch), end_time=from_epoch(end_time_epoch))

        cursor.execute('SELECT * FROM Giveaways WHERE GiveawayID in (' + parse_list(giveaways_by_id.keys()) + ')')
        data = cursor.fetchall()
        for row in data:
            # (giveaway_id, group_giveaway.link, group_giveaway.creator, group_giveaway.game_name, json.dumps(entries_data), json.dumps(group_giveaway.groups))
            giveaway_link = row[1]
            giveaway_id = StringUtils.get_hashed_id(giveaway_link)
            group_giveaways[giveaway_link] = giveaways_by_id[giveaway_id]
            group_giveaways[giveaway_link].link = giveaway_link
            group_giveaways[giveaway_link].creator = row[2]
            group_giveaways[giveaway_link].game_name = row[3]
            group_giveaways[giveaway_link].entries = dict()
            for ent_row in json.loads(row[4]):
                # (entry.user_name, entry.entry_time, entry.winner)
                user_name = ent_row[0]
                group_giveaways[giveaway_link].entries[user_name] = GiveawayEntry(user_name, entry_time=from_epoch(ent_row[1]), winner=ent_row[2])
            group_giveaways[giveaway_link].groups = json.loads(row[5])

    cursor.close()
    connection.close()
    LogUtils.log_info('Load Group ' + group_website + ' took ' + str(time.time() - start_time) + ' seconds')
    return Group(group_users, group_giveaways, cookies=cookies)


def get_all_groups():
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    groups = dict()
    cursor.execute("SELECT Name,Webpage FROM Groups")
    data = cursor.fetchall()
    for row in data:
        groups[row[0]] = row[1]

    cursor.close()
    connection.close()

    LogUtils.log_info('Get all groups took ' + str(time.time() - start_time) + ' seconds')
    return groups


def get_all_groups_with_users():
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    groups = dict()
    cursor.execute("SELECT Name,Webpage,Users FROM Groups WHERE Users<>'[]'")
    data = cursor.fetchall()
    for row in data:
        users = set()
        for user_data in json.loads(row[2]):
            # (group_user.user_name, group_user.group_won, group_user.group_sent)
            users.add(user_data[0])
        groups[row[0]] = Group(group_name=row[0], group_webpage=row[1], group_users=users)

    cursor.close()
    connection.close()

    LogUtils.log_info('Get all groups took ' + str(time.time() - start_time) + ' seconds')
    return groups


def check_existing_users(users_list):
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    existing_users = []
    cursor.execute('SELECT UserName FROM Users WHERE UserName IN (' + parse_list(users_list) + ')')
    data = cursor.fetchall()
    for row in data:
        existing_users.append(row[0])

    cursor.close()
    connection.close()

    LogUtils.log_info('Out of total ' + str(len(users_list)) + ' users in group, already exist in DB: ' + str(len(existing_users)))
    return existing_users


def get_user_data(user_name):
    group_user = None
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users WHERE UserName = "' + user_name + '"')
    data = cursor.fetchone()
    if data:
        # (group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent, group_user.level)
        group_user = GroupUser(user_name, steam_id=data[1], global_won=data[2], global_sent=data[3], level=data[4])

    cursor.close()
    connection.close()
    return group_user


def save_user(group_user):
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (UserName,SteamId,GlobalWon,GlobalSent,Level) '
                   'VALUES ("' + group_user.user_name + '","' + group_user.steam_id + '",' + str(group_user.global_won) + ',' + str(group_user.global_sent) + ',' + str(group_user.level) + ')')

    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()


def get_all_users():
    start_time = time.time()
    all_users = []
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users')
    data = cursor.fetchall()
    for row in data:
        # (group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent, group_user.level)
        group_user = GroupUser(row[0], steam_id=row[1], global_won=row[2], global_sent=row[3], level=row[4])
        all_users.append(group_user)

    cursor.close()
    connection.close()

    LogUtils.log_info('Get all users took ' + str(time.time() - start_time) + ' seconds')
    return all_users


def get_users_by_names(user_names):
    start_time = time.time()
    users_data = dict()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users WHERE UserName IN (' + parse_list(user_names) + ')')
    data = cursor.fetchall()
    for row in data:
        # (group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent, group_user.level)
        user_name = row[0]
        user_data = GroupUser(user_name, steam_id=row[1], global_won=row[2], global_sent=row[3], level=row[4])
        users_data[user_name] = user_data

    cursor.close()
    connection.close()

    LogUtils.log_info('Get users by name took ' + str(time.time() - start_time) + ' seconds')
    return users_data


def update_existing_users(users):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    users_data = []
    for user_data in users:
        users_data.append((user_data.steam_id, user_data.global_won, user_data.global_sent, user_data.level, user_data.user_name))

    cursor.executemany("UPDATE Users SET SteamId=%s,GlobalWon=%s,GlobalSent=%s,Level=%s WHERE UserName=%s", users_data)
    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    LogUtils.log_info('Update existing users for ' + str(len(users)) + ' users took ' + str(time.time() - start_time) + ' seconds')


def delete_users(users):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Users WHERE UserName IN(' + parse_list(list(map(lambda x: x.user_name, users))) + ')')
    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    LogUtils.log_info('Delete of ' + str(len(users)) + ' users took ' + str(time.time() - start_time) + ' seconds')


def get_existing_games_data(games_list):
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    existing_games_data = dict()
    cursor.execute("SELECT * FROM Games WHERE Name IN (" + parse_list(games_list) + ")")
    data = cursor.fetchall()
    for row in data:
        # (game.game_name, game.game_link, game.value, game.steam_score, game.num_of_reviews)
        game_name = row[0]
        game_data = GameData(game_name, row[1], row[2], steam_score=row[3], num_of_reviews=row[4])
        existing_games_data[game_name] = game_data

    cursor.close()
    connection.close()

    LogUtils.log_info('Out of total ' + str(len(games_list)) + ' games in group, already exist in DB: ' + str(len(existing_games_data)))
    return existing_games_data


def save_games(games):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    games_data = []
    for game in games:
        games_data.append((game.game_name, game.game_link, game.value, game.steam_score, game.num_of_reviews))

    cursor.executemany("INSERT IGNORE INTO Games (Name,LinkURL,Value,Score,NumOfReviews) VALUES (%s, %s, %s, %s, %s)", games_data)

    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    LogUtils.log_info('Save games for ' + str(len(games)) + ' games took ' + str(time.time() - start_time) + ' seconds')


def update_existing_games(games):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    games_data = []
    for game in games:
        games_data.append((game.game_link, game.value, game.steam_score, game.num_of_reviews, game.game_name))

    cursor.executemany("UPDATE Games SET LinkURL=%s,Value=%s,Score=%s,NumOfReviews=%s WHERE Name=%s", games_data)
    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    LogUtils.log_info('Update existing games for ' + str(len(games)) + ' games took ' + str(time.time() - start_time) + ' seconds')


def remove_games(games):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Games WHERE Name IN (' + parse_list(list(map(lambda x: x.game_name, games))) + ')')
    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    LogUtils.log_info('Delete of ' + str(len(games)) + ' invalid games took ' + str(time.time() - start_time) + ' seconds')


def get_game_data(game_name):
    game_data = None
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Games WHERE Name = "' + game_name + '"')
    data = cursor.fetchone()
    if data:
        # (game.game_name, game.game_link, game.value, game.steam_score, game.num_of_reviews)
        game_data = GameData(game_name, data[1], data[2], steam_score=data[3], num_of_reviews=data[4])

    cursor.close()
    connection.close()
    return game_data


def get_all_games():
    start_time = time.time()
    all_games = []
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Games')
    data = cursor.fetchall()
    for row in data:
        # (game.game_name, game.game_link, game.value, game.steam_score, game.num_of_reviews)
        game_data = GameData(row[0], row[1], row[2], steam_score=row[3], num_of_reviews=row[4])
        all_games.append(game_data)

    cursor.close()
    connection.close()

    LogUtils.log_info('Get list of all games took ' + str(time.time() - start_time) + ' seconds')
    return all_games


def save_empty_group(group_name, group_webpage, cookies):
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    cursor.execute('INSERT IGNORE INTO Groups (GroupID,Users,Giveaways,Name,Webpage,Cookies) '
                   'VALUES ("' + StringUtils.get_hashed_id(group_webpage) + '","[]","[]","' + group_name + '","' + group_webpage + '","' + to_str(cookies.replace('"','')) + '")')

    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()


def get_all_empty_groups():
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema, charset='utf8')
    cursor = connection.cursor()

    groups = dict()
    cursor.execute("SELECT Name,Webpage FROM Groups WHERE Users='[]' AND Giveaways='[]'")
    data = cursor.fetchall()
    for row in data:
        groups[row[0]] = row[1]

    cursor.close()
    connection.close()

    LogUtils.log_info('Get all empty groups took ' + str(time.time() - start_time) + ' seconds')
    return groups


def parse_list(list, prefix=''):
    result = ''
    if not list or len(list) == 0:
        return '""'
    for item in list:
        result += '"' + prefix + item + '",'

    return result[:-1]


def to_epoch(datetime_object):
    if datetime_object:
        return (datetime_object - datetime.datetime(1970, 1, 1)).total_seconds()
    return None


def from_epoch(time_in_epoch):
    if time_in_epoch or time_in_epoch == 0:
        return datetime.datetime.utcfromtimestamp(float(time_in_epoch))
    return None


def to_str(param):
    if not param:
        return ''
    return str(param)