# MySql connector of SGMT
# Copyright (C) 2017  Alex Milman
import calendar
import json
import pymysql
import hashlib
import ConfigParser

import time

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


def save_group(group_website, group):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
    cursor = connection.cursor()

    # Insert Giveaways
    giveaways_data = []
    group_giveaways_data = []
    for group_giveaway in group.group_giveaways.values():
        giveaway_id = get_hashed_id(group_giveaway.link)
        entries_data = []
        for entry in group_giveaway.entries.values():
            entries_data.append((entry.user_name, to_epoch(entry.entry_time), entry.winner))
        giveaways_data.append((giveaway_id, group_giveaway.link, group_giveaway.creator, group_giveaway.value, group_giveaway.game_name, json.dumps(entries_data), json.dumps(group_giveaway.groups)))
        group_giveaways_data.append((giveaway_id, to_epoch(group_giveaway.start_time), to_epoch(group_giveaway.end_time)))

    cursor.executemany("INSERT IGNORE INTO Giveaways (GiveawayID,LinkURL,Creator,Value,GameName,Entries,Groups) VALUES (%s,%s,%s,%s,%s,%s,%s)", giveaways_data)

    # Insert Users
    users_data = []
    group_users_data = []
    for group_user in group.group_users.values():
        users_data.append((group_user.user_name, group_user.steam_id, group_user.global_won, group_user.global_sent))
        group_users_data.append((group_user.user_name, group_user.group_won, group_user.group_sent))

    cursor.executemany("INSERT IGNORE INTO Users (UserName,SteamId,GlobalWon,GlobalSent) VALUES (%s, %s, %s, %s)", users_data)

    # Insert Group
    group_id = get_hashed_id(group_website)
    cursor.execute("INSERT IGNORE INTO Groups (GroupID,Users,Giveaways) VALUES (\"" + group_id + "\",\"" + json.dumps(group_users_data).replace('"','\\"') + "\",\"" + json.dumps(group_giveaways_data).replace('"','\\"') + "\")")

    connection.commit()  # you need to call commit() method to save your changes to the database

    cursor.close()
    connection.close()
    print "--- %s seconds ---" % (time.time() - start_time)


#TODO Implement optional params
def load_group(group_website, load_users_data=True, load_giveaway_data=True, limit_by_time=False, start_time=None, end_time=None):
    start_time = time.time()
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
    cursor = connection.cursor()

    # Load Group
    group_id = get_hashed_id(group_website)
    cursor.execute('SELECT * FROM Groups WHERE GroupID="' + group_id + '"')
    data = cursor.fetchone()
    group_users_data = json.loads(data[1])
    group_giveaways_data = json.loads(data[2])

    # Load Users Data
    group_users = dict()
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
    for row in group_giveaways_data:
        # (giveaway_id, calendar.timegm(group_giveaway.start_time), calendar.timegm(group_giveaway.end_time))
        giveaway_id = row[0]
        group_giveaways[giveaway_id] = GroupGiveaway(giveaway_id, start_time=from_epoch(row[1]), end_time=from_epoch(row[2]))

    cursor.execute('SELECT * FROM Giveaways WHERE GiveawayID in (' + parse_list(group_giveaways.keys()) + ')')
    data = cursor.fetchall()
    for row in data:
        # (giveaway_id, group_giveaway.link, group_giveaway.creator, group_giveaway.value, group_giveaway.game_name, json.dumps(entries_data), json.dumps(group_giveaway.groups))
        giveaway_id = row[0]
        group_giveaways[giveaway_id].link = row[1]
        group_giveaways[giveaway_id].creator = row[2]
        group_giveaways[giveaway_id].value = row[3]
        group_giveaways[giveaway_id].game_name = row[4]
        group_giveaways[giveaway_id].entries = dict()
        for ent_row in json.loads(row[5]):
            # (entry.user_name, entry.entry_time, entry.winner)
            user_name = ent_row[0]
            group_giveaways[giveaway_id].entries[user_name] = GiveawayEntry(user_name, entry_time=from_epoch(ent_row[1]), winner=ent_row[2])
        group_giveaways[giveaway_id].groups = json.loads(row[6])

    cursor.close()
    connection.close()
    print "--- %s seconds ---" % (time.time() - start_time)
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
                   'VALUES ("' + group_user.user_name + '","' + group_user.steam_id + '",' + group_user.global_won + ',' + group_user.global_sent + ')')

    cursor.close()
    connection.close()


def get_hashed_id(group_website):
    return hashlib.md5(group_website).hexdigest()


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