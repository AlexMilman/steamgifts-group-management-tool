# All constants for SteamGifts
# Copyright (C) 2017  Alex Milman


STEAMGIFTS_SEARCH_PAGE = '/search?page='
STEAMGIFTS_SEARCH_QUERY = '/search?q='
STEAMGIFTS_USER_LINK = 'https://www.steamgifts.com/user/'
STEAMGIFTS_GIVEAWAY_LINK = 'https://www.steamgifts.com/giveaway/'
STEAMGIFTS_LINK = 'https://www.steamgifts.com'


def get_steamgifts_users_page(group_webpage):
    return str(group_webpage) + '/users'


def get_giveaway_entries_link(partial_giveaway_link):
    return get_giveaway_link(partial_giveaway_link) + '/entries'


def get_giveaway_groups_link(partial_giveaway_link):
    return get_giveaway_link(partial_giveaway_link) + '/groups'


def get_giveaway_link(partial_giveaway_link):
    return STEAMGIFTS_LINK + str(partial_giveaway_link)


def get_user_link(user):
    return STEAMGIFTS_USER_LINK + user
