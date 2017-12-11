import time

import requests

from BusinessLogic.ScrapingUtils import SteamGiftsConsts, SteamConsts
from BusinessLogic.Utils import StringUtils, WebUtils
from Data.GameData import GameData
from Data.GiveawayEntry import GiveawayEntry
from Data.GroupGiveaway import GroupGiveaway
from Data.GroupUser import GroupUser

# All scraping implementations for SteamGifts
# Copyright (C) 2017  Alex Milman


def get_group_users(group_webpage, max_pages=0):
    group_users = dict()
    page_index = 1
    while page_index < max_pages or max_pages == 0:
        html_content = WebUtils.get_html_page(SteamGiftsConsts.get_steamgifts_users_page(group_webpage) + SteamGiftsConsts.STEAMGIFTS_SEARCH_QUERY + str(page_index))
        current_page_num = WebUtils.get_item_by_xpath(html_content, u'.//a[@class="is-selected"]/span/text()')
        if current_page_num and current_page_num != str(page_index):
            break

        user_elements = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="table__row-inner-wrap"]')
        for user_elem in user_elements:
            user = WebUtils.get_item_by_xpath(user_elem, u'.//a[@class="table__column__heading"]/text()')
            user_data_elements = WebUtils.get_items_by_xpath(user_elem, u'.//div[@class="table__column--width-small text-center"]/text()')
            user_sent = StringUtils.normalize_float(user_data_elements[0][0:user_data_elements[0].find('(')])
            user_received = StringUtils.normalize_float(user_data_elements[1][0:user_data_elements[1].find('(')])
            group_users[user] = GroupUser(user, user_received, user_sent)

        if not current_page_num:
            break

        page_index += 1

    return group_users


def update_user_additional_data(user):
    html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user.user_name))
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    user.steam_id = steam_user.split(SteamConsts.STEAM_PROFILE_LINK)[1]
    all_rows = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="featured__table__row"]')
    for row_content in all_rows:
        row_title = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__left"]/text()')
        if row_title == u'Gifts Won':
            user.global_won = StringUtils.normalize_int(WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__right"]/span/span/a/text()'))
        elif row_title == u'Gifts Sent':
            user.global_sent = StringUtils.normalize_int(WebUtils.get_item_by_xpath(row_content, u'.//div[@class=" featured__table__row__right"]/span/span/a/text()'))
        elif row_title == u'Contributor Level':
            user_level_item = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__right"]/span/@data-ui-tooltip')
            user.level = StringUtils.normalize_float(user_level_item.split('name" : "')[2].split('", "color')[0])


def get_group_giveaways(group_webpage, cookies, existing_giveaways=dict()):
    group_giveaways=dict()
    games=dict()
    reached_end=False
    giveaways_changed = True
    page_index = 1
    while not reached_end and giveaways_changed:
        giveaways_changed = False
        html_content = WebUtils.get_html_page(group_webpage + SteamGiftsConsts.STEAMGIFTS_SEARCH_QUERY + str(page_index))
        current_page_num = WebUtils.get_item_by_xpath(html_content, u'.//a[@class="is-selected"]/span/text()')
        if current_page_num and current_page_num != str(page_index):
            break

        giveaway_elements = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="giveaway__summary"]')
        for giveaway_elem in giveaway_elements:
            partial_giveaway_link = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__heading__name"]/@href')
            game_name = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__heading__name"]/text()').encode('utf-8')
            winners = WebUtils.get_items_by_xpath(giveaway_elem, u'.//div[@class="giveaway__column--positive"]/a/text()')
            poster = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__username"]/text()')
            timestamps = WebUtils.get_items_by_xpath(giveaway_elem, u'.//span/@data-timestamp')
            creation_time=None
            end_time=None
            if len(timestamps) >= 2:
                end_time = time.gmtime(StringUtils.normalize_float(timestamps[0]))
                creation_time = time.gmtime(StringUtils.normalize_float(timestamps[1]))

            giveaway_entries=dict()
            giveaway_entries_content = WebUtils.get_html_page(SteamGiftsConsts.get_giveaway_entries_link(partial_giveaway_link), cookies=cookies)
            giveaway_entries_elements = WebUtils.get_items_by_xpath(giveaway_entries_content, u'.//div[@class="table__row-inner-wrap"]')
            for entry_element in giveaway_entries_elements:
                entry_user = WebUtils.get_item_by_xpath(entry_element, u'.//a[@class="table__column__heading"]/text()').encode('utf-8')
                entry_time = time.gmtime(StringUtils.normalize_float(WebUtils.get_item_by_xpath(entry_element, u'.//div[@class="table__column--width-small text-center"]/span/@data-timestamp')))
                winner = False
                if entry_user in winners:
                    winner = True
                giveaway_entries[entry_user] = GiveawayEntry(entry_user, entry_time, winner=winner)

            giveaway_groups_content = WebUtils.get_html_page(SteamGiftsConsts.get_giveaway_groups_link(partial_giveaway_link), cookies=cookies)
            giveaway_groups = WebUtils.get_items_by_xpath(giveaway_groups_content, u'.//a[@class="table__column__heading"]/@href')

            giveaway_link = SteamGiftsConsts.get_giveaway_link(partial_giveaway_link)
            group_giveaway = GroupGiveaway(giveaway_link, game_name, poster, creation_time, end_time, giveaway_entries, giveaway_groups)

            steam_game_link = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__icon"]/@href')
            game_value = float(WebUtils.get_items_by_xpath(giveaway_elem, u'.//span[@class="giveaway__heading__thin"]/text()')[-1][1:-2])
            games[game_name] = GameData(game_name, steam_game_link, game_value)

            if giveaway_link not in existing_giveaways.keys() or not group_giveaway.equals(existing_giveaways[giveaway_link]):
                giveaways_changed = True
                group_giveaways[giveaway_link] = group_giveaway

            # if earliest_date and time.strftime('%Y-%m-%d', end_time) < earliest_date:
            #     reached_end = True
            #     break

        if not current_page_num or reached_end:
            break

        page_index += 1

    return group_giveaways, games


def get_monthly_posters(group_webpage, month, max_pages=0):
    monthly_giveaways=dict()
    posters=set()
    page_index = 1
    while page_index < max_pages or max_pages == 0:
        html_content = WebUtils.get_html_page(group_webpage + SteamGiftsConsts.STEAMGIFTS_SEARCH_QUERY + str(page_index))
        current_page_num = WebUtils.get_item_by_xpath(html_content, u'.//a[@class="is-selected"]/span/text()')
        if current_page_num and current_page_num != str(page_index):
            break

        giveaway_elements = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="giveaway__summary"]')
        for giveaway_elem in giveaway_elements:
            post_month = time.gmtime(StringUtils.normalize_float(WebUtils.get_item_by_xpath(giveaway_elem, u'.//span/@Data-timestamp'))).tm_mon
            if post_month == month:
                giveaway_link = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__heading__name"]/@href')
                poster = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__username"]/text()')
                if not monthly_giveaways[poster]:
                    monthly_giveaways[poster] = set()
                monthly_giveaways[poster].add(giveaway_link)

        if not current_page_num:
            break

        page_index += 1

    return posters


def test(cookies):
    WebUtils.get_page_content('https://www.steamgifts.com/giveaway/Rjkdw/sins-of-a-solar-empire-trinity', cookies)


def get_user_steam_id(user_name):
    html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user_name))
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    return steam_user.split(SteamConsts.STEAM_PROFILE_LINK)[1]


def get_steam_game_link(steamgifts_link, cookies):
    html_content = WebUtils.get_html_page(steamgifts_link, cookies)
    return WebUtils.get_item_by_xpath(html_content, u'.//a[@class="global__image-outer-wrap global__image-outer-wrap--game-large"]/@href')


def isValidLink(link):
    try:
        request = requests.get(link)
        if request.status_code == 200:
            return True
        else:
            return False
    except:
        return False

