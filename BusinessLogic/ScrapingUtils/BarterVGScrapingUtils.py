import json

from BusinessLogic.ScrapingUtils import BarterVGConsts
from BusinessLogic.Utils import WebUtils, LogUtils

# All scraping implementations for Barter.vg
# Copyright (C) 2020 Alex Milman


def get_free_games_list():
    LogUtils.log_info('Getting list of games previously given away for free')
    free_games_list = set()
    json_content = WebUtils.get_https_page_content(BarterVGConsts.FREE_GIVEAWAYS_JSON_LINK, unverified=True)
    all_free_games_dict = json.loads(json_content)
    for free_game_data in all_free_games_dict.values():
        if free_game_data['platform_id'] == 1:
            free_games_list.add(free_game_data['title'])

    return free_games_list