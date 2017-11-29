from BusinessLogic import WebUtils

# All scraping implementations for SteamRep
# Copyright (C) 2017  Alex Milman

steamrep_check_profile = 'https://steamrep.com/profiles/'

def check_user_not_public_or_banned(steam_user_id):
    html_content = WebUtils.get_html_page(get_steamrep_link(steam_user_id))
    privacy_status = WebUtils.get_item_by_xpath(html_content, u'.//span[@id="privacystate"]/span/text()')
    trade_ban_status = WebUtils.get_item_by_xpath(html_content, u'.//span[@id="tradebanstatus"]/span/text()')
    vac_ban_status = WebUtils.get_item_by_xpath(html_content, u'.//span[@id="vacbanned"]/span/text()')
    community_ban_status = WebUtils.get_item_by_xpath(html_content, u'.//span[@id="communitybanstatus"]/span/text()')
    no_special_reputation = WebUtils.get_item_by_xpath(html_content, u'.//div[@class="repbadge evilbox"]')

    return (privacy_status == 'Public' or privacy_status == '0') \
           and check_no_ban(trade_ban_status) and check_no_ban(vac_ban_status) \
           and check_no_ban(community_ban_status) and no_special_reputation is None

def check_no_ban(trade_ban_status):
    return trade_ban_status == 'None' or trade_ban_status == '---'


def get_steamrep_link(user_id):
    return steamrep_check_profile + user_id