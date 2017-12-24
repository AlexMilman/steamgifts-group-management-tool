# Game object used to hold all game data
# Copyright (C) 2017  Alex Milman


class GameData(object):
    game_name=''
    game_link=''
    value=0.0
    num_of_reviews=-1
    steam_score=-1

    def __init__(self, game_name, game_link, value, num_of_reviews=-1, steam_score=-1):
        self.game_name = game_name
        self.game_link = game_link
        self.value = float(value)
        self.num_of_reviews = int(num_of_reviews)
        self.steam_score = int(steam_score)

    def equals(self, game):
        return self.game_name == game.game_name\
                and self.game_link == game.game_link\
                and self.value == game.value\
                and self.num_of_reviews == game.num_of_reviews\
                and self.steam_score == game.steam_score