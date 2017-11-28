# GroupUser object used to all group users data
# Copyright (C) 2017  Alex Milman

class GroupUser(object):
    user_name=None
    won_games=0.0
    sent_games=0.0
    steam_id=None

    def __init__(self, user_name, won_games=0.0, sent_games=0.0):
        self.user_name = user_name
        self.won_games = won_games
        self.sent_games = sent_games
