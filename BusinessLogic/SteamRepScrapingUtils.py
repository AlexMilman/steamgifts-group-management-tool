from BusinessLogic import StringUtils, SteamGiftsScrapingUtils
from BusinessLogic.BaseScraper import BaseScraper
from lxml import html

# All scraping implementations for SteamRep
# Copyright (C) 2017  Alex Milman

steamrep_check_profile = 'https://steamrep.com/profiles/'

class SteamRepScraper(BaseScraper):

    def __init__(self):
        pass

    def check_user_not_public_or_banned(self, steam_user_id):
        html_content = self.get_html_page(get_steamrep_link(steam_user_id))
        privacy_status = self.get_item_by_xpath(html_content, u'.//span[@id="privacystate"]/span/text()')
        trade_ban_status = self.get_item_by_xpath(html_content, u'.//span[@id="tradebanstatus"]/span/text()')
        vac_ban_status = self.get_item_by_xpath(html_content, u'.//span[@id="vacbanned"]/span/text()')
        community_ban_status = self.get_item_by_xpath(html_content, u'.//span[@id="communitybanstatus"]/span/text()')
        no_special_reputation = self.get_item_by_xpath(html_content, u'.//div[@class="norep reptag"]')

        return privacy_status != 'Public' and trade_ban_status != 'None' and vac_ban_status != 'None' and community_ban_status != 'None' and no_special_reputation

def get_steamrep_link(user_id):
    return steamrep_check_profile + user_id