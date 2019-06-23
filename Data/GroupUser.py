# GroupUser object used to all group users data
# Copyright (C) 2017  Alex Milman


class GroupUser(object):
    user_name=''
    steam_id=None
    steam_user_name=None

    def __init__(self, user_name, steam_id=None, steam_user_name=None):
        self.user_name = user_name
        self.steam_id = steam_id
        self.steam_user_name = steam_user_name

    def equals(self, user):
        return self.user_name == user.user_name\
                and self.steam_id == user.steam_id\
                and self.steam_user_name == user.steam_user_name