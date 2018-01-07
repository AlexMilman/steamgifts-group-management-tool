from BusinessLogic.ScrapingUtils import SteamConsts, SteamDBConsts
from BusinessLogic.Utils import WebUtils, StringUtils, LogUtils


# All scraping implementations for SteamDB pages
# Copyright (C) 2017  Alex Milman


def get_game_additional_data(game_name, game_link):
    LogUtils.log_info('Processing game in SteamDB: ' + game_name)
    steam_score = 0
    num_of_reviews = 0
    steam_app_id = game_link.split(SteamConsts.STEAM_GAME_LINK)[1]
    html_content = WebUtils.get_html_page(SteamDBConsts.STEAM_DB_APP_LINK + steam_app_id, https=True)
    steam_game_tooltip = WebUtils.get_item_by_xpath(html_content, u'.//span[@class="header-thing header-thing-good tooltipped tooltipped-n"]/@aria-label')
    if steam_game_tooltip != 'Need more user reviews to generate a score' and steam_game_tooltip != 'No user reviews':
        steam_score = int(StringUtils.normalize_float(steam_game_tooltip.split('%')[0]))
        num_of_reviews = StringUtils.normalize_int(steam_game_tooltip.split('of the')[1].split('user reviews')[0])
    return steam_score, num_of_reviews
