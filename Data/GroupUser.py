# GroupUser object used to all group users data
# Copyright (C) 2017  Alex Milman


class GroupUser(object):
    user_name=None
    group_won=0.0
    group_sent=0.0
    global_won=0.0
    global_sent=0.0
    steam_id=None

    def __init__(self, user_name, group_won=0.0, group_sent=0.0, global_won=0.0, global_sent=0.0):
        self.user_name = user_name
        self.group_won = group_won
        self.group_sent = group_sent
        self.global_won = global_won
        self.global_sent = global_sent
