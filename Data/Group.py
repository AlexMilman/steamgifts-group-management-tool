# Group object used to hold all group data
# Copyright (C) 2017  Alex Milman

class Group(object):
    group_users=dict()
    group_giveaways=dict()

    def __init__(self, group_users=dict(), group_giveaways=dict()):
        self.group_users = group_users
        self.group_giveaways = group_giveaways