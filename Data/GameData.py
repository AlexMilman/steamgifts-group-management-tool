# Game object used to hold all game data
# Copyright (C) 2017  Alex Milman


class GameData(object):
    num_of_reviews=0
    steam_score=0

    def __init__(self, num_of_reviews=0, steam_score=0):
        self.num_of_reviews = num_of_reviews
        self.steam_score = steam_score
