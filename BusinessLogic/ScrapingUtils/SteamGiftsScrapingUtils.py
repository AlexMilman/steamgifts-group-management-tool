from datetime import datetime
import requests
import ConfigParser
import json

from BusinessLogic.ScrapingUtils import SteamGiftsConsts, SteamConsts
from BusinessLogic.Utils import StringUtils, WebUtils, LogUtils
from Data.BundledGame import BundledGame
from Data.GameData import GameData
from Data.GiveawayEntry import GiveawayEntry
from Data.GroupGiveaway import GroupGiveaway
from Data.GroupUser import GroupUser

# All scraping implementations for SteamGifts
# Copyright (C) 2017  Alex Milman

config = ConfigParser.ConfigParser()
config.read('application.config')
delay_time = float(config.get('Web', 'Delay'))
failures_threshold = int(config.get('Web', 'FailuresThreshold'))


def get_group_users(group_webpage):
    LogUtils.log_info('Processing users for group ' + group_webpage)
    group_users = dict()
    page_index = 1
    while True:
        LogUtils.log_info('Processing users page #' + str(page_index))
        users_page_url = SteamGiftsConsts.get_steamgifts_users_page(group_webpage) + SteamGiftsConsts.STEAMGIFTS_SEARCH_PAGE + str(page_index)
        html_content = WebUtils.get_html_page(users_page_url, delay=delay_time)
        if html_content is None:
            LogUtils.log_error('Cannot process users page: ' + users_page_url)
            break
        current_page_num = WebUtils.get_item_by_xpath(html_content, u'.//a[@class="is-selected"]/span/text()')
        if current_page_num and current_page_num != str(page_index):
            break

        user_elements = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="table__row-outer-wrap"]')
        for user_elem in user_elements:
            user = WebUtils.get_item_by_xpath(user_elem, u'.//a[@class="table__column__heading"]/text()')
            group_users[user] = GroupUser(user)

        if not current_page_num:
            break

        page_index += 1

    LogUtils.log_info('Finished processing users for group ' + group_webpage)
    return group_users


def update_user_additional_data(user):
    LogUtils.log_info('Processing SteamGifts user ' + user.user_name)
    html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user.user_name), delay=delay_time)
    if html_content is None:
        LogUtils.log_error('Cannot update additional data for user: ' + user.user_name)
        return False
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    if not steam_user:
        LogUtils.log_error('Cannot update non-existent user: ' + user.user_name)
        return False
    user.steam_id = steam_user.split(SteamConsts.STEAM_PROFILE_LINK)[1]

    user_menu_rows = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="featured__table__row"]')
    for row_content in user_menu_rows:
        user_menu_type = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__left"]/text()')
        if user_menu_type == 'Registered':
            data_timestamp = float(WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__right"]/span/@data-timestamp'))
            user.creation_time = datetime.fromtimestamp(data_timestamp)
            break

    return True


def get_group_giveaways(group_webpage, cookies, existing_giveaways=None, force_full_run=False, start_date=None, end_date=None):
    if existing_giveaways is None:
        existing_giveaways = dict()
    LogUtils.log_info('Starting to process giveaways for group ' + group_webpage)
    group_giveaways=dict()
    ignored_giveaways=[]
    games=dict()
    reached_end=False
    giveaways_changed=True
    reached_ended_giveaways=False
    page_index = 1
    reached_threshold=False
    while not reached_end and not reached_threshold and (giveaways_changed or not reached_ended_giveaways or force_full_run):
        giveaways_changed = False
        reached_ended_giveaways = False
        giveaways_page_url = group_webpage + SteamGiftsConsts.STEAMGIFTS_SEARCH_PAGE + str(page_index)
        html_content = WebUtils.get_html_page(giveaways_page_url, delay=delay_time)
        if html_content is None:
            LogUtils.log_error('Cannot process page: ' + giveaways_page_url)
            break
        current_page_num = WebUtils.get_item_by_xpath(html_content, u'.//a[@class="is-selected"]/span/text()')
        if current_page_num and current_page_num != str(page_index):
            break
        if current_page_num:
            LogUtils.log_info('Processing giveaways page ' + get_page_num_str(current_page_num))

        giveaway_elements = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="giveaway__summary"]')
        if end_date:
            earliest_end_time = datetime.utcfromtimestamp(StringUtils.normalize_float(WebUtils.get_items_by_xpath(giveaway_elements[-1], u'.//span/@data-timestamp')[0]))
            if earliest_end_time and earliest_end_time > datetime.strptime(end_date, '%Y-%m-%d'):
                page_index += 1
                continue

        failures = 0
        for giveaway_elem in giveaway_elements:
            if failures >= failures_threshold:
                reached_threshold = True
                break
            giveaway_not_started_yet = False
            giveaway_ended = False
            for end_time_text in WebUtils.get_items_by_xpath(giveaway_elem, u'.//div/text()'):
                if end_time_text == ' Begins in ':
                    giveaway_not_started_yet = True
                if end_time_text == 'Ended ':
                    giveaway_ended = True

            partial_giveaway_link = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__heading__name"]/@href')
            giveaway_link = SteamGiftsConsts.get_giveaway_link(partial_giveaway_link)
            LogUtils.log_info('Starting to process ' + giveaway_link)
            game_name = extract_game_name(giveaway_elem)
            if not game_name:
                continue
            winners = get_and_encode_list(giveaway_elem, u'.//div[@class="giveaway__column--positive"]/a/text()')
            poster = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__username"]/text()').encode('utf-8')
            num_of_entries = WebUtils.get_items_by_xpath(giveaway_elem, u'.//div[@class="giveaway__links"]/a/span/text()')[0].split(" ")[0]
            timestamps = WebUtils.get_items_by_xpath(giveaway_elem, u'.//span/@data-timestamp')
            creation_time=None
            end_time=None
            if len(timestamps) >= 2:
                if giveaway_not_started_yet:
                    creation_time = datetime.utcfromtimestamp(StringUtils.normalize_float(timestamps[0]))
                else:
                    end_time = datetime.utcfromtimestamp(StringUtils.normalize_float(timestamps[0]))
                    creation_time = datetime.utcfromtimestamp(StringUtils.normalize_float(timestamps[1]))

            existing_giveaway = existing_giveaways.get(giveaway_link)
            if not existing_giveaway:
                LogUtils.log_info("NEW giveaway found: " + giveaway_link)
            if giveaway_ended and existing_giveaway and existing_giveaway.get_winners() == winners:
                ignored_giveaways.append(giveaway_link)
                continue

            if winners:
                reached_ended_giveaways = True

            if len(winners) >= 3:
                giveaway_winners_link = SteamGiftsConsts.get_giveaway_winners_link(partial_giveaway_link)
                winners_content = WebUtils.get_html_page(giveaway_winners_link, cookies=cookies, delay=delay_time)
                if winners_content is not None:
                    error_message = WebUtils.get_item_by_xpath(winners_content, u'.//div[@class="page__heading__breadcrumbs"]/text()')
                    if not error_message or error_message != 'Error':
                        current_winners_page_num = WebUtils.get_item_by_xpath(winners_content, u'.//a[@class="is-selected"]/span/text()')
                        LogUtils.log_info('Processing ' + giveaway_link + ' winners page ' + get_page_num_str(current_winners_page_num))
                        winners.extend(get_and_encode_list(winners_content, u'.//p[@class="table__column__heading"]/a/text()'))

                        if current_winners_page_num:
                            winners_page_index = 2
                            while True:
                                winners_url = giveaway_winners_link + SteamGiftsConsts.STEAMGIFTS_SEARCH_PAGE + str(winners_page_index)
                                winners_content = WebUtils.get_html_page(winners_url, cookies=cookies, delay=delay_time)
                                if winners_content is None:
                                    LogUtils.log_error('Cannot process page: ' + winners_url)
                                    failures += 1
                                    break
                                current_winners_page_num = WebUtils.get_item_by_xpath(winners_content, u'.//a[@class="is-selected"]/span/text()')
                                if current_winners_page_num and current_winners_page_num != str(winners_page_index):
                                    break
                                LogUtils.log_info('Processing ' + giveaway_link + ' winners page ' + get_page_num_str(current_winners_page_num))
                                winners.extend(get_and_encode_list(winners_content, u'.//p[@class="table__column__heading"]/a/text()'))
                                winners_page_index += 1
                else:
                    failures += 1
                    ignored_giveaways.append(giveaway_link)
                    LogUtils.log_warning('Unable to process winners for ' + giveaway_winners_link)
                    continue

            giveaway_entries=dict()
            if not giveaway_not_started_yet and \
                    (not existing_giveaway or len(existing_giveaway.entries) != int(num_of_entries.replace(',','')) or existing_giveaway.get_winners() != winners):
                giveaway_entries_link = SteamGiftsConsts.get_giveaway_entries_link(partial_giveaway_link)
                entries_content = WebUtils.get_html_page(giveaway_entries_link, cookies=cookies, delay=delay_time)
                if entries_content is not None:
                    error_message = WebUtils.get_item_by_xpath(entries_content, u'.//div[@class="page__heading__breadcrumbs"]/text()')
                    if not error_message or error_message != 'Error':
                        current_entries_page_num = WebUtils.get_item_by_xpath(entries_content, u'.//a[@class="is-selected"]/span/text()')
                        LogUtils.log_info('Processing ' + giveaway_link + ' entries page ' + get_page_num_str(current_entries_page_num))
                        process_entries(entries_content, giveaway_entries, winners)

                        if current_entries_page_num:
                            entries_page_index = 2
                            while True:
                                entries_url = giveaway_entries_link + SteamGiftsConsts.STEAMGIFTS_SEARCH_PAGE + str(entries_page_index)
                                entries_content = WebUtils.get_html_page(entries_url, cookies=cookies, delay=delay_time)
                                if entries_content is None:
                                    LogUtils.log_error('Cannot process page: ' + entries_url)
                                    break
                                current_entries_page_num = WebUtils.get_item_by_xpath(entries_content, u'.//a[@class="is-selected"]/span/text()')
                                if current_entries_page_num and current_entries_page_num != str(entries_page_index):
                                    break
                                LogUtils.log_info('Processing ' + giveaway_link + ' entries page ' + get_page_num_str(current_entries_page_num))
                                process_entries(entries_content, giveaway_entries, winners)
                                entries_page_index += 1
                    else:
                        LogUtils.log_warning('Error processing entries for ' + giveaway_link)
                        # We can't access the GA data, but we can still know who won
                        for entry_user in winners:
                            giveaway_entries[entry_user] = GiveawayEntry(entry_user, datetime.utcfromtimestamp(0), winner=True)
                else:
                    failures += 1
                    ignored_giveaways.append(giveaway_link)
                    LogUtils.log_warning('Unable to process entries for ' + giveaway_entries_link)
                    continue

            elif existing_giveaway:
                giveaway_entries = existing_giveaway.entries

            if existing_giveaway:
                giveaway_groups = existing_giveaway.groups
            else:
                giveaway_groups_link = SteamGiftsConsts.get_giveaway_groups_link(partial_giveaway_link)
                giveaway_groups_content = WebUtils.get_html_page(giveaway_groups_link, cookies=cookies, delay=delay_time)
                if giveaway_groups_content is not None:
                    giveaway_groups = get_and_encode_list(giveaway_groups_content, u'.//a[@class="table__column__heading"]/@href')
                else:
                    failures += 1
                    ignored_giveaways.append(giveaway_link)
                    LogUtils.log_warning('Unable to process groups for ' + giveaway_groups_link)
                    continue

            group_giveaway = GroupGiveaway(giveaway_link, game_name, poster, creation_time, end_time, giveaway_entries, giveaway_groups)

            steam_game_link = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__icon"]/@href')
            game_value = float(WebUtils.get_items_by_xpath(giveaway_elem, u'.//span[@class="giveaway__heading__thin"]/text()')[-1][1:-2])
            games[game_name] = GameData(game_name, steam_game_link, game_value)

            if giveaway_link in existing_giveaways and group_giveaway.equals(existing_giveaways[giveaway_link]):
                ignored_giveaways.append(giveaway_link)
            else:
                giveaways_changed = True
                if giveaway_link in existing_giveaways and existing_giveaways[giveaway_link].start_time != group_giveaway.start_time:
                    group_giveaway.start_time = existing_giveaways[giveaway_link].start_time
                group_giveaways[giveaway_link] = group_giveaway

            if start_date:
                if end_time and end_time < datetime.strptime(start_date, '%Y-%m-%d'):
                    reached_end = True
                    break

        if not current_page_num or reached_end:
            break

        page_index += 1

    LogUtils.log_info('Finished processing giveaways for group ' + group_webpage)
    return group_giveaways, ignored_giveaways, games, reached_threshold


def get_bundled_games_data():
    bundled_games_data = []
    page_index = 1
    steamgifts_bundled_games_response = json.loads(WebUtils.get_page_content(SteamGiftsConsts.STEAMGIFTS_BUNDLED_GAMES_LINK, delay=delay_time))
    while steamgifts_bundled_games_response['success'] and steamgifts_bundled_games_response['results']:
        LogUtils.log_info('Processing bundled games page #' + str(page_index))
        bundled_games = steamgifts_bundled_games_response['results']
        for bundled_game in bundled_games:
            bundled_games_data.append(BundledGame(bundled_game['app_id'], bundled_game['name'], bundled_game['package_id'], bundled_game['reduced_value_timestamp'], bundled_game['no_value_timestamp']))
        page_index += 1
        steamgifts_bundled_games_response = json.loads(WebUtils.get_page_content(SteamGiftsConsts.STEAMGIFTS_BUNDLED_GAMES_LINK + SteamGiftsConsts.STEAMGIFTS_BUNDLED_GAMES_PAGE + str(page_index), delay=delay_time))

    return bundled_games_data


def extract_game_name(giveaway_elem):
    game_name = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__heading__name"]/text()', default='').encode('utf-8')
    if not game_name:
        game_name = WebUtils.get_item_by_xpath(giveaway_elem, u'.//a[@class="giveaway__heading__name"]/text()', default='').decode('utf-8','ignore').encode("utf-8")
    game_name.replace('"', '\"')
    return game_name


def get_and_encode_list(element, xpath):
    results = []
    for item in WebUtils.get_items_by_xpath(element, xpath):
        results.append(item.encode('utf-8'))
    return results


def is_giveaway_deleted(giveaway_link, cookies):
    LogUtils.log_info('Checking if giveaway was deleted: ' + giveaway_link)
    giveaway_content = WebUtils.get_html_page(giveaway_link, cookies=cookies, delay=delay_time)
    if giveaway_content is not None:
        error_messages = WebUtils.get_items_by_xpath(giveaway_content,u'.//div[@class="table__column--width-fill"]/text()')
        if error_messages and len(error_messages) >= 4 and error_messages[0].startswith('Deleted'):
            return True
    return False


def process_entries(entries_content, giveaway_entries, winners):
    entries_elements = WebUtils.get_items_by_xpath(entries_content, u'.//div[@class="table__row-inner-wrap"]')
    for entry_element in entries_elements:
        entry_user = WebUtils.get_item_by_xpath(entry_element, u'.//a[@class="table__column__heading"]/text()').encode('utf-8')
        entry_timestamp = WebUtils.get_item_by_xpath(entry_element,u'.//div[@class="table__column--width-small text-center"]/span/@data-timestamp')
        entry_time = datetime.utcfromtimestamp(StringUtils.normalize_float(entry_timestamp))
        winner = False
        if entry_user in winners:
            winner = True
        giveaway_entries[entry_user] = GiveawayEntry(entry_user, entry_time, winner=winner)


def get_page_num_str(page_num):
    if page_num:
        return '#' + str(page_num)
    return ''


def test(cookies):
    WebUtils.get_page_content('https://www.steamgifts.com/giveaway/Rjkdw/sins-of-a-solar-empire-trinity', cookies)


def get_group_name(group_webpage, cookies=None):
    html_content = WebUtils.get_html_page(group_webpage, cookies=cookies)
    return WebUtils.get_item_by_xpath(html_content, u'.//div[@class="featured__heading__medium"]/text()')


def is_user_in_group(user, groups_to_check):
    for group in groups_to_check:
        search_user_url = SteamGiftsConsts.get_steamgifts_users_page(SteamGiftsConsts.get_giveaway_link(group)) + SteamGiftsConsts.STEAMGIFTS_SEARCH_QUERY + user
        html_content = WebUtils.get_html_page(search_user_url, delay=delay_time)
        found_user = WebUtils.get_item_by_xpath(html_content, u'.//a[@class="table__column__heading"]/text()')
        if user == found_user:
            return True
    return False


def isValidLink(link):
    try:
        request = requests.get(link)
        if request.status_code == 200:
            return True
        else:
            return False
    except:
        return False


### Only used for checking user validity ###
def get_user_steam_id(user_name):
    html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user_name))
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    return steam_user.split(SteamConsts.STEAM_PROFILE_LINK)[1]


def get_user_contribution_data(user_name):
    html_content = WebUtils.get_html_page(SteamGiftsConsts.get_user_link(user_name))
    if html_content is None:
        LogUtils.log_error('Cannot update additional data for user: ' + user_name)
        return None
    steam_user = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="sidebar__shortcut-inner-wrap"]/a/@href')
    if not steam_user:
        LogUtils.log_error('Cannot update non-existent user: ' + user_name)
        return None

    global_won = -1
    global_sent = -1
    level = -1
    all_rows = WebUtils.get_items_by_xpath(html_content, u'.//div[@class="featured__table__row"]')
    for row_content in all_rows:
        row_title = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__left"]/text()')
        if row_title == u'Gifts Won':
            global_won = StringUtils.normalize_int(WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__right"]/span/span/a/text()'))
        elif row_title == u'Gifts Sent':
            global_sent = StringUtils.normalize_int(WebUtils.get_item_by_xpath(row_content, u'.//div[@class=" featured__table__row__right"]/span/span/a/text()'))
        elif row_title == u'Contributor Level':
            user_level_item = WebUtils.get_item_by_xpath(row_content, u'.//div[@class="featured__table__row__right"]/span/@data-ui-tooltip')
            level = StringUtils.normalize_float(user_level_item.split('name" : "')[2].split('", "color')[0])

    if global_won or global_sent or level:
        return global_won, global_sent, level

    return None
