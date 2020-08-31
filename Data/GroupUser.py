# GroupUser object used to all group users data
# Copyright (C) 2017  Alex Milman


class GroupUser(object):
    user_name=''
    steam_id=None
    steam_user_name=None
    creation_time=None

    def __init__(self, user_name, steam_id=None, steam_user_name=None, creation_time=None):
        self.user_name = user_name
        self.steam_id = steam_id
        self.steam_user_name = steam_user_name
        self.creation_time = creation_time

    def equals(self, user):
        return self.user_name == user.user_name\
            and self.steam_id == user.steam_id\
            and self.steam_user_name == user.steam_user_name                \
            and self.creation_time == user.creation_time