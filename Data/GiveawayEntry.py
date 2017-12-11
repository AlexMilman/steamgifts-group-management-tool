# GroupEntry object used to hold all group giveaway entries data
# Copyright (C) 2017  Alex Milman


class GiveawayEntry(object):
    user_name=''
    entry_time=None
    winner=False

    def __init__(self, user_name, entry_time=None, winner=False):
        self.user_name = user_name.encode('utf-8')
        self.entry_time = entry_time
        self.winner = winner