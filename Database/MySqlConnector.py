# MySql connector of SGMT
# Copyright (C) 2017  Alex Milman
import calendar
import json
import pymysql
import ConfigParser

import time

from BusinessLogic.Utils import StringUtils
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
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
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
        giveaways_data.append((giveaway_id, group_giveaway.link, group_giveaway.creator, group_giveaway.value, group_giveaway.game_name, json.dumps(entries_data), json.dumps(group_giveaway.groups)))

    cursor.executemany("INSERT INTO Giveaways (GiveawayID,LinkURL,Creator,Value,GameName,Entries,Groups) VALUES (%s,%s,%s,%s,%s,%s,%s)"\
                       + " ON DUPLICATE KEY UPDATE LinkURL=VALUES(LinkURL),Creator=VALUES(Creator),Value=VALUES(Value),GameName=VALUES(GameName),Entries=VALUES(Entries),Groups=VALUES(Groups)", giveaways_data)

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
            users_data.append((group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent))

    cursor.executemany("INSERT IGNORE INTO Users (UserName,SteamId,GlobalWon,GlobalSent) VALUES (%s, %s, %s, %s)", users_data)

    # Merge with existing group data (in case of update/merge)
    if existing_group_data and existing_group_data.group_users:
        for existing_user_data in existing_group_data.group_users.values():
            if existing_user_data.user_name not in group.group_users.keys():
                group_users_data.append((existing_user_data.user_name, existing_user_data.group_won, existing_user_data.group_sent))

    # Insert Group
    group_id_str = "\"" + StringUtils.get_hashed_id(group_website) + "\""
    group_users_data_str = "\"" + json.dumps(group_users_data).replace('"', '\\"') + "\""
    group_giveaways_data_str = "\"" + json.dumps(group_giveaways_data).replace('"', '\\"') + "\""
    cursor.execute("INSERT INTO Groups (GroupID,Users,Giveaways) VALUES (" + group_id_str + "," + group_users_data_str + "," + group_giveaways_data_str + ")"\
                  "  ON DUPLICATE KEY UPDATE Users=VALUES(Users),Giveaways=VALUES(Giveaways)")

    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    print 'Save Group ' + group_website + ' took ' + str(time.time() - start_time) +  ' seconds'


#TODO Implement optional params
def load_group(group_website, load_users_data=True, load_giveaway_data=True, limit_by_time=False, start_time=None, end_time=None):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
    cursor = connection.cursor()

    # Load Group
    group_id = StringUtils.get_hashed_id(group_website)
    cursor.execute('SELECT * FROM Groups WHERE GroupID="' + group_id + '"')
    data = cursor.fetchone()
    group_users_data = json.loads(data[1])
    group_giveaways_data = json.loads(data[2])

    # Load Users Data
    group_users = dict()
    if load_users_data:
        for row in group_users_data:
            # (group_user.user_name, group_user.group_won, group_user.group_sent)
            user_name = row[0]
            group_users[user_name] = GroupUser(user_name, group_won=row[1], group_sent=row[2])

        cursor.execute('SELECT * FROM Users WHERE UserName in (' + parse_list(group_users.keys()) + ')')
        data = cursor.fetchall()
        for row in data:
            # (group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent)
            user_name = row[0]
            group_users[user_name].steam_id=row[1]
            group_users[user_name].global_won=row[2]
            group_users[user_name].global_sent=row[3]

    # Load Giveaways Data
    group_giveaways = dict()
    giveaways_by_id=dict()
    if load_giveaway_data:
        for row in group_giveaways_data:
            # (giveaway_id, calendar.timegm(group_giveaway.start_time), calendar.timegm(group_giveaway.end_time))
            giveaway_id = row[0]
            giveaways_by_id[giveaway_id] = GroupGiveaway(giveaway_id, start_time=from_epoch(row[1]), end_time=from_epoch(row[2]))

        cursor.execute('SELECT * FROM Giveaways WHERE GiveawayID in (' + parse_list(giveaways_by_id.keys()) + ')')
        data = cursor.fetchall()
        for row in data:
            # (giveaway_id, group_giveaway.link, group_giveaway.creator, group_giveaway.value, group_giveaway.game_name, json.dumps(entries_data), json.dumps(group_giveaway.groups))
            giveaway_link = row[1]
            giveaway_id = StringUtils.get_hashed_id(giveaway_link)
            group_giveaways[giveaway_link] = giveaways_by_id[giveaway_id]
            group_giveaways[giveaway_link].link = giveaway_link
            group_giveaways[giveaway_link].creator = row[2]
            group_giveaways[giveaway_link].value = row[3]
            group_giveaways[giveaway_link].game_name = row[4]
            group_giveaways[giveaway_link].entries = dict()
            for ent_row in json.loads(row[5]):
                # (entry.user_name, entry.entry_time, entry.winner)
                user_name = ent_row[0]
                group_giveaways[giveaway_link].entries[user_name] = GiveawayEntry(user_name, entry_time=from_epoch(ent_row[1]), winner=ent_row[2])
            group_giveaways[giveaway_link].groups = json.loads(row[6])

    cursor.close()
    connection.close()
    print 'Load Group ' + group_website + ' took ' + str(time.time() - start_time) +  ' seconds'
    return Group(group_users, group_giveaways)


def check_existing_users(users_list):
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
    cursor = connection.cursor()

    existing_users = []
    cursor.execute("SELECT UserName FROM Users WHERE UserName IN (" + parse_list(users_list) + ")")
    data = cursor.fetchall()
    for row in data:
        existing_users.append(row[0])

    cursor.close()
    connection.close()
    return existing_users


def get_user_data(user_name):
    group_user = None
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users WHERE UserName = "' + user_name + '"')
    data = cursor.fetchone()
    if data:
        # (group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent)
        group_user = GroupUser(user_name, steam_id=data[1], global_won=data[2], global_sent=data[3])

    cursor.close()
    connection.close()
    return group_user


def save_user(group_user):
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (UserName,SteamId,GlobalWon,GlobalSent) '
                   'VALUES ("' + group_user.user_name + '","' + group_user.steam_id + '",' + str(group_user.global_won) + ',' + str(group_user.global_sent) + ')')

    cursor.close()
    connection.close()


def parse_list(list, prefix=''):
    result = ''
    for item in list:
        result += '"' + prefix + item + '",'

    return result[:-1]


def to_epoch(time_object):
    if time_object:
        return calendar.timegm(time_object)
    return None


def from_epoch(time_in_epoch):
    if time_in_epoch:
        return time.gmtime(time_in_epoch)
    return None