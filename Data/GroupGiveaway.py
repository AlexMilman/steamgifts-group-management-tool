# GroupGiveaway object used to hold all group giveaways data
# Copyright (C) 2017  Alex Milman


class GroupGiveaway(object):
    link=None
    creator=''
    value=0.0
    start_date=None
    end_date=None
    game_name=''
    entries=dict()
    groups=[]

    def __init__(self, link, creator, value, start_date=None, end_date=None, entries=dict(), groups=[]):
        self.link = link
        self.creator = creator
        self.value = value
        self.start_date = start_date
        self.end_date = end_date
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
                winners.append(entry)
        return winners
