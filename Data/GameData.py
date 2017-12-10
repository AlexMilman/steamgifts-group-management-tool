# Game object used to hold all game data
# Copyright (C) 2017  Alex Milman


class GameData(object):
    game_name=''
    game_link=''
    value=0.0
    num_of_reviews=0
    steam_score=0

    def __init__(self, game_name, game_link, value, num_of_reviews=0, steam_score=0):
        self.game_name = game_name
        self.game_link = game_link
        self.value = float(value)
        self.num_of_reviews = int(num_of_reviews)
        self.steam_score = int(steam_score)
