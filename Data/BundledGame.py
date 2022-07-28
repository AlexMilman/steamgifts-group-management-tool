# BundledGame object used to hold data of a bundled game
# Copyright (C) 2022  Alex Milman


class BundledGame(object):
    app_id=None
    bundle_id=None
    game_name=''
    was_bundled=False
    was_free=False

    def __init__(self, app_id, bundle_id, game_name, was_bundled, was_free):
        self.app_id = app_id
        self.bundle_id = bundle_id
        self.game_name = game_name.encode('utf-8')
        self.was_bundled = bool(was_bundled)
        self.was_free = bool(was_free)
