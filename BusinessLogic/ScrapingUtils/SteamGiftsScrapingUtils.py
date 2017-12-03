import time

import requests

from BusinessLogic.ScrapingUtils import SteamGiftsConsts, SteamConsts
from BusinessLogic.Utils import StringUtils, WebUtils
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


def get_group_giveaways(group_webpage, cookies=None, earliest_date=None):
    group_giveaways=dict()
    reached_end=False
    page_index = 1
    while not reached_end:
        html_content = WebUtils.get_html_page(group_webpage + SteamGiftsConsts.STEAMGIFTS_SEARCH_QUERY + str(page_index))
        current_page_num = WebUtils.get_item_by_xpath(html_content, u'.//a[@class="is-selected"]/span/text()')
        if current_page_num and current_page_num != str(page_index):
            break

        giveaway_elements = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="giveaway__summary"]')
        for giveaway_elem in giveaway_elements:
            giveaway_link = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__heading__name"]/@href')
            winners = WebUtils.get_items_by_xpath(giveaway_elem, u'.//div[@class="giveaway__column--positive"]/a/text()')
            poster = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__username"]/text()')
            timestamps = WebUtils.get_items_by_xpath(giveaway_elem, u'.//span/@data-timestamp')
            creation_time=None
            end_time=None
            if len(timestamps) >= 2:
                end_time = time.localtime(StringUtils.normalize_float(timestamps[0]))
                creation_time = time.localtime(StringUtils.normalize_float(timestamps[1]))

            giveaway_entries=[]
            giveaway_groups=[]
            if cookies:
                giveaway_entries_content = WebUtils.get_html_page(SteamGiftsConsts.get_giveaway_entries_link(giveaway_link), cookies=cookies)
                giveaway_entries = WebUtils.get_items_by_xpath(giveaway_entries_content, u'.//a[@class="table__column__heading"]/text()')

                giveaway_groups_content = WebUtils.get_html_page(SteamGiftsConsts.get_giveaway_groups_link(giveaway_link), cookies=cookies)
                giveaway_groups = WebUtils.get_items_by_xpath(giveaway_groups_content, u'.//a[@class="table__column__heading"]/@href')

            group_giveaways[SteamGiftsConsts.get_giveaway_link(giveaway_link)] = (GroupGiveaway(SteamGiftsConsts.get_giveaway_link(giveaway_link), poster, creation_time, end_time, giveaway_entries, giveaway_groups, winners))

            if earliest_date and time.strftime('%Y-%m-%d', end_time) < earliest_date:
                reached_end = True
                break

        if not current_page_num or reached_end:
            break

        page_index += 1

    return group_giveaways


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
            post_month = time.localtime(StringUtils.normalize_float(WebUtils.get_item_by_xpath(giveaway_elem, u'.//span/@Data-timestamp'))).tm_mon
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


def check_users_steamgifts_ratio(group_users):
    users_with_negative_ratio=[]
    for user in group_users:
        html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user))
        all_rows = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="featured__table__row"]')
        for row_content in all_rows:
            row_title = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__left"]/text()')
            if row_title == u'Gifts Won':
                gifts_won = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__right"]/span/span/a/text()')
            elif row_title == u'Gifts Sent':
                gifts_sent = WebUtils.get_item_by_xpath(row_content, u'.//div[@class=" featured__table__row__right"]/span/span/a/text()')

        if gifts_won and gifts_sent and StringUtils.normalize_int(gifts_won) > StringUtils.normalize_int(gifts_sent):
            users_with_negative_ratio.append(SteamGiftsConsts.get_user_link(user))

    return users_with_negative_ratio


def test(cookies):
    WebUtils.get_page_content('https://www.steamgifts.com/giveaway/Rjkdw/sins-of-a-solar-empire-trinity', cookies)


def get_user_steam_id(user_name):
    html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user_name))
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    return steam_user.split(SteamConsts.STEAM_PROFILE_LINK)[1]


def update_user_additional_data(user):
    html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user.user_name))
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    user.steam_id = steam_user.split(SteamConsts.STEAM_PROFILE_LINK)[1]
    all_rows = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="featured__table__row"]')
    for row_content in all_rows:
        row_title = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__left"]/text()')
        if row_title == u'Gifts Won':
            user.global_win = StringUtils.normalize_int(WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__right"]/span/span/a/text()'))
        elif row_title == u'Gifts Sent':
            user.global_sent = StringUtils.normalize_int(WebUtils.get_item_by_xpath(row_content, u'.//div[@class=" featured__table__row__right"]/span/span/a/text()'))


def isValidLink(link):
    try:
        request = requests.get(link)
        if request.status_code == 200:
            return True
        else:
            return False
    except:
        return False






