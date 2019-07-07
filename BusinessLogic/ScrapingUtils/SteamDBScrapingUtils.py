from BusinessLogic.ScrapingUtils import SteamConsts, SteamDBConsts
from BusinessLogic.Utils import WebUtils, StringUtils, LogUtils


# All scraping implementations for SteamDB pages
# Copyright (C) 2017  Alex Milman


def get_game_additional_data(game_name, game_link):
    LogUtils.log_info('Processing game in SteamDB: ' + game_name)
    steam_score = 0
    num_of_reviews = 0
    steam_app_id = game_link.split(SteamConsts.STEAM_GAME_LINK)[1].split('/')[0]
    html_content = WebUtils.get_html_page(SteamDBConsts.STEAM_DB_APP_LINK + steam_app_id, https=True)
    steam_score_positive = WebUtils.get_item_by_xpath(html_content, u'.//span[@class="header-thing-good"]/text()')
    steam_score_negative = WebUtils.get_item_by_xpath(html_content, u'.//span[@class="header-thing-poor"]/text()')

    if steam_score_positive and steam_score_negative:
        positive_score = int(steam_score_positive)
        negative_score = int(steam_score_negative)
        num_of_reviews = positive_score + negative_score
        steam_score = int(float(positive_score) / num_of_reviews * 100)
    return steam_score, num_of_reviews
