from lxml import html

from BusinessLogic.ScrapingUtils import SteamGiftsScrapingUtils
from BusinessLogic.Utils import WebUtils

# All scraping implementations for Steam & SteamFinder pages
# Copyright (C) 2017  Alex Milman

steam_filter_link = 'https://steamcommunity.com/linkfilter/?url='
steam_profile_link = 'http://steamcommunity.com/profiles/'
steam_user_id_link = 'http://steamcommunity.com/id/'
steam_search_query = '/?ctp='
steamfinder_lookup_link = 'https://steamidfinder.com/lookup/'


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
        page_content = WebUtils.get_page_content(steam_after_n_thread_link + steam_search_query + str(page_index))
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

            if steam_profile_link in steam_user:
                steam_id = steam_user.split(steam_profile_link)[1]
            else:
                page_content = WebUtils.get_page_content(steamfinder_lookup_link + steam_user.split(steam_user_id_link)[1])
                partial_page = page_content[:page_content.find('" target="_blanl"')]
                steam_id = partial_page[partial_page.find('<br>profile <code><a href="') + 27:].split(steam_profile_link)[1]

            # Check if steam_id is currently in SG group
            if steam_id in steam_id_to_user:
                user = steam_id_to_user[steam_id]
                giveaway_links = WebUtils.get_items_by_xpath(gifter_elem, u'.//div[@class="commentthread_comment_text"]/a/@href')
                for giveaway_link in giveaway_links:
                    giveaway_link = str(giveaway_link).replace(steam_filter_link, '')
                    if (giveaway_link in giveaways.keys() and giveaways[giveaway_link].creator == user and giveaway_link
                        and giveaway_link.startswith(SteamGiftsScrapingUtils.steamgifts_giveaway_link)):
                        if user not in after_n_giveaways:
                            after_n_giveaways[user] = set()
                        after_n_giveaways[user].add(giveaway_link)

        if page_end == page_total:
            break
        page_index += 1

    return after_n_giveaways


def get_user_steam_id(user):
    html_content = WebUtils.get_html_page(SteamGiftsScrapingUtils.get_user_link(user))
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    return steam_user.split(steam_profile_link)[1]

