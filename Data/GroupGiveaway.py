# GroupGiveaway object used to hold all group giveaways data
# Copyright (C) 2017  Alex Milman


class GroupGiveaway(object):
    link=None
    creator=''
    value=0.0
    start_date=None
    end_date=None
    game_name=''
    entries=[]
    groups=[]
    winners=[]

    def __init__(self, link, creator, value, start_date=None, end_date=None, entries=[], groups=[], winners=[]):
        self.link = link
        self.creator = creator
        self.value = value
        self.start_date = start_date
        self.end_date = end_date
        self.entries = entries
        self.groups = groups
        self.winners = winners
