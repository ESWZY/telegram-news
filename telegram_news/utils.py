# -*- coding: UTF-8 -*-

"""
This module provides some utilities for development.

Add new ones when possible.
"""

import json
import xmltodict
from bs4 import BeautifulSoup

try:
    import urlparse
    from urllib import urlencode
except Exception:  # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode


def keep_img(text, url):
    """
    Remove tags except media <img>.

    :param text: raw text string.
    :param url: base url of the website.
    :return: processed string.
    """
    soup = BeautifulSoup(text, 'lxml')
    # print(text)

    # Keep the first blank if have
    blank_num = 0
    if text[0] == ' ':
        blank_num = 1

    # No image here, return directly
    if not soup.select('img'):
        return ' ' * blank_num + soup.getText().replace('<', '&lt;').replace('>', '&gt;')

    # Find image(s)
    else:
        # Copy from original text
        cp = str(soup)

        # The target string
        result = ""

        # Remove other tags, except <a>
        for img in soup.select('img'):

            # Split the text by <img> tag
            other = str(cp).split(str(img))

            # Get the image url
            img_link = img.get('src')

            # Get plain text and concatenate with link
            result += BeautifulSoup(other[0], 'lxml').getText().strip().replace('<', '&lt;').replace('>', '&gt;')
            if img_link:
                # If the image link is a relative path
                img_link = get_full_link(img_link, url)

                # Embed the image as a link
                result += '<a href=\"' + img_link + '\">' + '[Media]' + '</a>'

            # Remove the processed text from processing string
            cp = str(cp).replace(str(other[0]) + str(img), "")

        # Return processed text and the plain text behind
        return ' ' * blank_num + result + BeautifulSoup(cp, 'lxml').getText().replace('<', '&lt;').replace('>', '&gt;')


def keep_link(text, url):
    """
    Remove tags except <a></a> and <img>. Otherwise, Telegram API will not parse.

    :param text: raw text string.
    :param url: base url of the website.
    :return: processed string.
    """
    if not text:
        return ""
    text = text.replace('<br>', '\n')
    soup = BeautifulSoup(text, 'lxml')

    # No link here, return directly
    if not soup.select('a'):
        return keep_img(text, url)

    # Find link(s)
    else:

        # Copy from original text
        cp = str(soup)

        # The target string
        result = ""

        # Remove other tags, except <a>
        for link in soup.select('a'):

            # Split the text by <a> tag
            other = str(cp).split(str(link))

            # Get the link url
            content = link.get_text().replace('<', '&lt;').replace('>', '&gt;')
            link_url = link.get('href')

            # Get plain text and concatenate with link
            result += keep_img(other[0], url)

            # Not keep <a> without any text or link
            if content:
                if link_url:
                    link_url = get_full_link(link_url, url)
                    result += '<a href=\"' + link_url + '\">' + str(content) + '</a>'
                else:
                    str(content)

            # Remove the processed text from processing string
            cp = str(cp).replace(str(other[0]) + str(link), "")

        # Return processed text and the plain text behind
        return result + keep_img(cp, url)


def is_single_media(text):
    """
    Judge whether the paragraph is an single media.

    :param text: one paragraph string.
    :return: bool.
    """
    soup = BeautifulSoup(text, 'lxml')

    # No <a> tag here, return directly
    if not soup.select('a'):
        return False
    else:
        anchor = soup.select('a')[0]

        if anchor.getText() == '[Media]':
            if text.replace(str(anchor), '') == '':
                return True
    return False


def str_url_encode(text):
    """
    Encode package before send to Telegram API.

    :param text: string.
    :return: string.
    """
    return urlparse.quote(text)


def get_full_link(link, base_url):
    """
    Parse the relative link to absolute link.

    :param link: relative path or absolute path.
    :param base_url: base url.
    :return: full url.
    """
    if link is not None:
        return urlparse.urljoin(base_url, link)
    else:
        return ''


def add_parameters_into_url(url, parameters):
    """
    Add parameters onto url. The url might already have GET parameters. parameters in a dict.

    :param url: url string.
    :param parameters: dict.
    :return: url string.
    """
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(parameters)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)


def xml_to_json(xml_str):
    """
    Convert from XML format string to JSON format string.

    :param xml_str: XML format string.
    :return: JSON format string.
    """
    xml_parse = xmltodict.parse(xml_str)
    json_str = json.dumps(xml_parse)
    return json_str


def get_full_width(text, get_full_width_char, get_full_width_number, get_full_width_symbol):
    """
    Get full width characters.

    :param text: original text.
    :param get_full_width_char: set True to get full width English letter.
    :param get_full_width_number: set True to get full width number.
    :param get_full_width_symbol: set True to get full width symbol.
    :return: full width text result.
    """

    if get_full_width_char:
        set1 = {chr(0x0041 + i): chr(0xFF21 + i) for i in range(26)}    # A -> Ａ
        set2 = {chr(0x0061 + i): chr(0xFF41 + i) for i in range(26)}    # a -> ａ
        text = text.translate(str.maketrans(set1))
        text = text.translate(str.maketrans(set2))
    if get_full_width_number:
        text = text.translate(str.maketrans({chr(0x0030 + i): chr(0xFF10 + i) for i in range(10)}))
    if get_full_width_symbol:
        set3 = {'!': '！', '"': '＂', '#': '＃', '$': '＄', '%': '％', '&': '＆', "'": '＇', '(': '（', ')': '）',
                '*': '＊', '+': '＋', ',': '，', '-': '－', '.': '．', '/': '／', ':': '：', ';': '；', '<': '＜',
                '=': '＝', '>': '＞', '?': '？', '@': '＠', '[': '［', '\\': '＼', ']': '］', '^': '＾', '_': '＿',
                '`': '｀', '{': '｛', '|': '｜', '}': '｝', '~': '～'}
        text = text.translate(str.maketrans(set3))
    return text
