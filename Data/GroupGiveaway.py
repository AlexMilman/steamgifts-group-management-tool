# GroupGiveaway object used to hold all group giveaways data
# Copyright (C) 2017  Alex Milman


class GroupGiveaway(object):
    link=None
    game_name=''
    creator=''
    start_time=None
    end_time=None
    entries=dict()
    groups=[]

    def __init__(self, link, game_name='', creator='', start_time=None, end_time=None, entries=None, groups=None):
        if groups is None:
            groups = []
        if entries is None:
            entries = dict()
        self.link = link
        self.game_name = game_name
        self.creator = creator.encode('utf-8')
        self.start_time = start_time
        self.end_time = end_time
        self.entries = entries
        self.groups = groups

    def has_winners(self):
        for entry in self.entries.values():
            if entry.winner:
                return True
        return False

    def get_winners(self):
        winners=[]
        for entry in self.entries.values():
            if entry.winner:
                winners.append(entry.user_name)
        return winners

    def equals(self, giveaway):
        return self.link == giveaway.link\
        and self.game_name == giveaway.game_name\
        and self.creator == giveaway.creator\
        and self.start_time == giveaway.start_time\
        and self.end_time == giveaway.end_time\
        and self.entries_equals(giveaway.entries)\
        and set(self.groups) == set(giveaway.groups)

    def entries_equals(self, entries):
        if len(entries) != len(self.entries):
            return False
        for foreign_entry in entries.values():
            if foreign_entry.user_name not in self.entries.keys():
                return False
            local_entry = self.entries[foreign_entry.user_name]
            if local_entry.entry_time != foreign_entry.entry_time or local_entry.winner != foreign_entry.winner:
                return False
        return True
