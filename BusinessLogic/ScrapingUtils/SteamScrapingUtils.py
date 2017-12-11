from lxml import html

from BusinessLogic.ScrapingUtils import SteamFinderScrapingUtils, SteamConsts, SteamGiftsConsts
from BusinessLogic.Utils import WebUtils, StringUtils


# All scraping implementations for SteamFinder pages
# Copyright (C) 2017  Alex Milman


def get_steam_id_to_user_dict(users):
    steam_id_to_user=dict()
    for user in users:
        steam_id_to_user[user.steam_id] = user.user_name
    return steam_id_to_user


def verify_after_n_giveaways(steam_after_n_thread_link, giveaways, group_users, max_pages=0):
    after_n_giveaways = dict()
    steam_id_to_user = get_steam_id_to_user_dict(group_users.values())
    page_index = 1
    while page_index < max_pages or max_pages == 0:
        page_content = WebUtils.get_page_content(steam_after_n_thread_link + SteamConsts.STEAM_SEARCH_QUERY + str(page_index))
        partial_page = page_content[page_content.find('_pageend') + 10:]
        page_end = partial_page[:partial_page.find('</span>')]
        partial_page = page_content[page_content.find('_pagetotal') + 12:]
        page_total = partial_page[:partial_page.find('</span>')]

        html_content = html.fromstring(page_content)
        gifter_elemens = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="commentthread_comment responsive_body_text  "]')
        for gifter_elem in gifter_elemens:
            steam_user = WebUtils.get_item_by_xpath(gifter_elem, u'.//a[@class="hoverunderline commentthread_author_link "]/@href')
            if not steam_user:
                continue  # this means this is the creator of the thread

            if SteamConsts.STEAM_PROFILE_LINK in steam_user:
                steam_id = steam_user.split(SteamConsts.STEAM_PROFILE_LINK)[1]
            else:
                steam_id = SteamFinderScrapingUtils.get_steam_id(steam_user)
            # Check if steam_id is currently in SG group
            if steam_id in steam_id_to_user:
                user = steam_id_to_user[steam_id]
                giveaway_links = WebUtils.get_items_by_xpath(gifter_elem, u'.//div[@class="commentthread_comment_text"]/a/@href')
                for giveaway_link in giveaway_links:
                    giveaway_link = str(giveaway_link).replace(SteamConsts.STEAM_FILTER_LINK, '')
                    if (giveaway_link in giveaways.keys() and giveaways[giveaway_link].creator == user and giveaway_link
                        and giveaway_link.startswith(SteamGiftsConsts.STEAMGIFTS_GIVEAWAY_LINK)):
                        if user not in after_n_giveaways:
                            after_n_giveaways[user] = set()
                        after_n_giveaways[user].add(giveaway_link)

        if page_end == page_total:
            break
        page_index += 1

    return after_n_giveaways


def update_game_additional_data(game):
    html_content = WebUtils.get_html_page(game.game_link, "birthtime=-7199; lastagecheckage=1-January-1970; mature_content=1;")
    steam_game_tooltip = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="user_reviews_summary_row"]/@data-store-tooltip')[-1]
    if steam_game_tooltip != 'Need more user reviews to generate a score':
        game.steam_score = StringUtils.normalize_int(steam_game_tooltip.split('%')[0])
        game.num_of_reviews = StringUtils.normalize_int(steam_game_tooltip.split('of the')[1].split('user reviews')[0])
