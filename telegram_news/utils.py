# -*- coding: UTF-8 -*-

"""
This module provides some utilities for development.

Add new ones when possible.
"""

import json
import re
import os
import requests
import math
import hashlib

import xmltodict
from bs4 import BeautifulSoup

try:
    import urlparse
    from urlparse import (
        urlunparse,
        parse_qsl,
        urljoin,
    )
    from urllib import (
        urlencode,
        quote,
        URLopener
    )
except Exception:  # For Python 3
    from urllib.parse import (
        urlparse,
        urlunparse,
        parse_qsl,
        urljoin,
        urlencode,
        quote
    )
    from urllib.request import URLopener

try:
    from urllib.request import (
        urlretrieve,
        urlopen
    )
except Exception:
    from urllib import (
        urlretrieve,
        urlopen
    )


def keep_media(text, url, with_link=True):
    """
    Remove tags except media tags.

    :param text: raw text string.
    :param url: base url of the website.
    :return: processed string.
    """
    if not text:
        return ''

    text = '<div>' + text + '</div>'  # text = '</div>blabla<div>'

    soup = BeautifulSoup(text, 'lxml')
    # print(text)

    # Keep the first blank if have
    blank_num = 0
    if text[0] == ' ':
        blank_num = 1

    # No media here, return directly
    if not soup.select('img, video'):
        return ' ' * blank_num + soup.getText().replace('<', '&lt;').replace('>', '&gt;')

    # Find media
    else:
        # Copy from original text
        cp = str(soup)

        # The target string
        result = ""

        media_list = soup.select('img, video')

        # Remove other tags, except <a>
        for media in media_list:

            # Split the text by <img> tag and <video> tag
            other = str(cp).split(str(media))

            # Get the media url
            media_link = media.get('src')

            # Get plain text and concatenate with link
            result += BeautifulSoup(other[0], 'lxml').getText().strip().replace('<', '&lt;').replace('>', '&gt;')
            if media_link:
                # If the media link is a relative path
                media_link = get_full_link(media_link, url)

                if with_link:
                    # Embed the media as a link
                    result += '<a href=\"' + media_link + '\">' + '[Media]' + '</a>'
                else:
                    result += '[Media]'

            # Remove the processed text from processing string
            cp = str(cp).replace(str(other[0]) + str(media), "")

        # Return processed text and the plain text behind
        return ' ' * blank_num + result + BeautifulSoup(cp, 'lxml').getText().replace('<', '&lt;').replace('>', '&gt;')


def keep_img(text, url, with_link=True):
    return keep_media(text, url, with_link)


def keep_link(text, url, with_media_link=True):
    """
    Remove tags except <a></a>, <img> and <video>. Otherwise, Telegram API will not parse.

    :param with_media_link: boolean, whether keep media symbol link.
    :param text: raw text string.
    :param url: base url of the website.
    :return: processed string.
    """
    if not text:
        return ""

    text = text.replace('<br>', '\n')
    text = text.replace('<br/>', '\n')
    text = text.replace('<br[/s]*?/>', '\n')

    # Ignore HTML comment
    text = re.sub(r'<!--[\s\S]*?-->', '', text)

    soup = BeautifulSoup(text, 'lxml')

    # No link here, return directly
    if not soup.select('a'):
        return keep_media(text, url, with_media_link)

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
            result += keep_media(other[0], url, with_media_link)

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
        return result + keep_media(cp, url, with_media_link)


def is_single_media(text):
    """
    Judge whether the paragraph is an single media.

    :param text: one paragraph string.
    :return: bool.
    """
    soup = BeautifulSoup(text, 'lxml')

    # ONE <a> tag here, return True
    if soup.select('a'):
        anchor = soup.select('a')[0]

        if anchor.getText() == '[Media]':
            if text.replace(str(anchor), '') == '':
                return True

    # ONE media plain stmbol here, return True
    elif text.strip() == '[Media]':
        return True

    return False


def str_url_encode(text):
    """
    Encode package before send to Telegram API.

    :param text: string.
    :return: string.
    """
    return quote(text)


def get_full_link(link, base_url):
    """
    Parse the relative link to absolute link.

    :param link: relative path or absolute path.
    :param base_url: base url.
    :return: full url.
    """
    if link is not None:
        return urljoin(base_url, link)
    else:
        return ''


def add_parameters_into_url(url, parameters):
    """
    Add parameters onto url. The url might already have GET parameters. parameters in a dict.

    :param url: url string.
    :param parameters: dict.
    :return: url string.
    """
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(parameters)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


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
        set1 = {chr(0x0041 + i): chr(0xFF21 + i) for i in range(26)}  # A -> Ａ
        set2 = {chr(0x0061 + i): chr(0xFF41 + i) for i in range(26)}  # a -> ａ
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


def get_hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def get_image_from_select(tags_select, link):
    images = []
    for img in tags_select:
        if img.get('src'):
            images.append(get_full_link(img.get('src'), link))
        elif img.get('data-src'):
            images.append(get_full_link(img.get('data-src'), link))  # For lazy loading
        elif img.find('source'):
            if img.find('source').get('srcset'):
                images.append(get_full_link(img.find('source').get('srcset'), link))
            elif img.find('source').get('data-srcset'):
                images.append(get_full_link(img.find('source').get('data-srcset'), link))  # For lazy loading
    return images


def get_video_from_select(tags_select, link):
    videos = []
    for vid in tags_select:
        if vid.get('src'):
            videos.append(get_full_link(vid.get('src'), link))
        elif vid.find('source'):
            if vid.find('source').get('src'):
                videos.append(get_full_link(vid.find('source').get('src'), link))
    return videos


def download_file_by_url(url, filename=None, header=None):
    if not filename:
        filename = os.path.basename(urlparse(url).path)
    if os.path.exists(filename):
        return
    r = requests.get(url, headers=header)
    with open(filename, 'wb') as f:
        f.write(r.content)


def get_network_file(url):
    return urlopen(url)


def get_ext_from_url(url):
    path = urlparse(url).path
    return os.path.splitext(path)[1]


def extract_video_config(video_full_name, thumb_full_name):
    """Get configs and thumbnail of the video, by OpenCV."""
    try:
        import cv2
    except ModuleNotFoundError:
        print('You do not have cv2 module, please install by yourself!')
        return False, 0, 640, 360

    cam = cv2.VideoCapture(video_full_name)

    duration = cam.get(cv2.CAP_PROP_FRAME_COUNT) / cam.get(cv2.CAP_PROP_FPS)
    width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

    success, image = cam.read()
    if success:
        cv2.imwrite(thumb_full_name, image)
        return True, math.ceil(duration), int(width), int(height)
    return False, math.ceil(duration), int(width), int(height)


def detect_and_download_video(url, path, name):
    """Detect and download video in page, return video name, by Youtube-DL."""
    try:
        import youtube_dl
    except ModuleNotFoundError:
        print('You do not have youtube-dl, please install by yourself!')
        return None

    # Specific file name, disable logs and warnings
    ydl_opts = {'outtmpl': os.path.join(path, name) + '.%(ext)s', 'quiet': True, 'no_warnings': True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(url, download=True)
        except Exception:
            return None

    if len(meta['entries']) > 0:
        return name + '.' + meta['entries'][0]['ext']
    else:
        return None


def get_file_length(url):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        if 'Content-Length' in res.headers:
            return res.headers['Content-Length']
        else:
            return -1
    else:
        return 0
