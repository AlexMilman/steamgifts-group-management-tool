from BusinessLogic.ScrapingUtils import SteamFinderConsts, SteamConsts
from BusinessLogic.Utils import WebUtils

# All scraping implementations for SteamFinder pages
# Copyright (C) 2017  Alex Milman



def get_steam_id(steam_user_link):
    steam_alt_user_id = steam_user_link.split(SteamConsts.STEAM_USER_ID_LINK)[1]
    page_content = WebUtils.get_page_content(SteamFinderConsts.STEAMFINDER_LOOKUP_LINK + steam_alt_user_id)
    partial_page = page_content[:page_content.find('" target="_blanl"')]
    steam_id = partial_page[partial_page.find('<br>profile <code><a href="') + 27:].split(SteamConsts.STEAM_USER_ID_LINK)[1]
    return steam_id
