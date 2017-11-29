import httplib
import urllib2
from lxml import html

# WebUtils module responsible for web page downloads, and xpath traversal
# Copyright (C) 2017  Alex Milman

def get_items_by_xpath(image_data, xpath_param, default=None):
    xpath_value = image_data.xpath(xpath_param)
    if xpath_value is not None:
        return xpath_value
    return default


def get_item_by_xpath(image_data, xpath_param, default=None):
    xpath_value = image_data.xpath(xpath_param)
    if isinstance(xpath_value, list):
        if len(xpath_value) > 0:
            return xpath_value[0]
        else:
            return default
    else:
        return xpath_value.extract()


def get_html_page(page_url, cookies=None):
    return html.fromstring(get_page_content(page_url, cookies))


def get_page_content(page_url, cookies=None):
    page_url = page_url.encode('utf-8')
    content = ""
    opener = urllib2.build_opener()
    if cookies:
        opener.addheaders.append(('Cookie', cookies))
    response = opener.open(page_url)
    while 1:
        try:
            data = response.read()
        except httplib.IncompleteRead, e:
            content = e.partial
            break
        if not data:
            break
        content += data
    return content

