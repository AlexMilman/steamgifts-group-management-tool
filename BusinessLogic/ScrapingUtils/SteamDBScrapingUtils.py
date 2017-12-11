from BusinessLogic.ScrapingUtils import SteamConsts, SteamDBConsts
from BusinessLogic.Utils import WebUtils

# All scraping implementations for SteamDB pages
# Copyright (C) 2017  Alex Milman


def update_game_additional_data(game):
    steam_app_id = game.game_link.split(SteamConsts.STEAM_GAME_LINK)[1]
    html_content = WebUtils.get_html_page(SteamDBConsts.STEAM_DB_APP_LINK + steam_app_id)
    # steam_game_tooltip = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="user_reviews_summary_row"]/@data-store-tooltip')[-1]
    # if steam_game_tooltip != 'Need more user reviews to generate a score' and steam_game_tooltip != 'No user reviews':
    #     game.steam_score = StringUtils.normalize_int(steam_game_tooltip.split('%')[0])
    #     game.num_of_reviews = StringUtils.normalize_int(steam_game_tooltip.split('of the')[1].split('user reviews')[0])