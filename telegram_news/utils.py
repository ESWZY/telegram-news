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

from .constant import (
    MAX_THUMB_SIZE
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
    text = re.sub('<br[\s]*?/>', '\n', text)

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
                    result += '<a href=\"' + link_url + '\">' + str(content).strip() + '</a>'
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
    xml_str = re.sub(r'<\?[\s\S]*?\?>', '', xml_str)
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


def download_file_by_url(url, filename, header=None, max_retry=10):
    if not filename:
        filename = os.path.basename(urlparse(url).path)
    if os.path.exists(filename):
        return

    # Retry only when there is no network error
    max_retry = max_retry
    while max_retry:
        try:
            # Use requests.get to download target file, and write to a new file.
            r = requests.get(url, headers=header)
            if r.status_code != 200:
                print('File not found!', url)
                return
            with open(filename, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print('Download file ' + url + ' failed (' + str(e) + ')! Retry ' + str(max_retry) + ' time(s).')
            max_retry -= 1
            continue
        break


def get_network_file(url):
    return urlopen(url)


def get_ext_from_url(url):
    path = urlparse(url).path
    return os.path.splitext(path)[1]


def save_compressed_image(image, image_full_path, size_upper_bound):
    """
    Compress image files to `size_upper_bound`kb.
    Need OpenCV, only (at least for now) be called by `extract_video_config`
    :param image: binary image
    :param image_full_path: path to save
    :param size_upper_bound: max image size
    """
    try:
        import cv2
    except ModuleNotFoundError:
        print('You do not have cv2 module, please install by yourself!')
        return

    cv2.imwrite(image_full_path, image)
    begin_quality = 100
    while os.path.getsize(image_full_path) > size_upper_bound * 1000:
        print(size_upper_bound * 1000 / os.path.getsize(image_full_path))
        begin_quality = begin_quality * (size_upper_bound * 1000 / os.path.getsize(image_full_path)) - 1
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), begin_quality]
        result, encimg = cv2.imencode('.jpg', image, encode_param)
        decimg = cv2.imdecode(encimg, 1)
        if result:
            cv2.imwrite(image_full_path, decimg)


def save_compressed_video(video_full_path, size_upper_bound, two_pass=True, filename_suffix='1'):
    """
    Compress video file to max-supported size.
    :param video_full_path: the video you want to compress.
    :param size_upper_bound: Max video size in B.
    :param two_pass: Set to True to enable two-pass calculation.
    :param filename_suffix: Add a suffix for new video.
    :return: out_put_name or error
    """
    if not os.path.exists(video_full_path):
        return False
    if os.path.getsize(video_full_path) <= size_upper_bound:
        return video_full_path

    try:
        import ffmpeg
    except ModuleNotFoundError:
        print('You do not have ffmpeg-python module, please install it by yourself!')
        return False

    filename, extension = os.path.splitext(video_full_path)
    extension = '.mp4'
    output_file_name = filename + filename_suffix + extension

    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000

    try:
        # Bitrate reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
        probe = ffmpeg.probe(video_full_path)
        # Video duration, in s.
        duration = float(probe['format']['duration'])
        # Audio bitrate, in bps.
        audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), {'bit_rate': 0})['bit_rate'])
        # Target total bitrate, in bps.
        target_total_bitrate = (size_upper_bound * 8) / (1.073741824 * duration)
        if target_total_bitrate < total_bitrate_lower_bound:
            print('Bitrate is extremely low! Stop compress!')
            return False

        # Best min size, in B.
        best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / 8
        if size_upper_bound < best_min_size:
            print('Quality not good! Recommended minimum size:', '{:,}'.format(int(best_min_size)), 'B.')
            # return False

        # Target audio bitrate, in bps.
        audio_bitrate = audio_bitrate

        # target audio bitrate, in bps
        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = target_total_bitrate / 10
            if audio_bitrate < min_audio_bitrate < target_total_bitrate:
                audio_bitrate = min_audio_bitrate
            elif audio_bitrate > max_audio_bitrate:
                audio_bitrate = max_audio_bitrate

        # Target video bitrate, in bps.
        video_bitrate = target_total_bitrate - audio_bitrate
        if video_bitrate < 1000:
            # TODO: keep audio only?
            print('Bitrate {} is extremely low! Stop compress.'.format(video_bitrate))
            return False

        i = ffmpeg.input(video_full_path)
        if two_pass:
            ffmpeg.output(i, '/dev/null' if os.path.exists('/dev/null') else 'NUL',
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                          ).overwrite_output().run()
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()
        else:
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()

        if os.path.getsize(output_file_name) <= size_upper_bound:
            return output_file_name
        elif os.path.getsize(output_file_name) < os.path.getsize(video_full_path):  # Do it again
            return save_compressed_video(output_file_name, size_upper_bound)
        else:
            return False
    except FileNotFoundError as e:
        # `sudo apt install ffmpeg` / `brew install ffmpeg`, or install by yourself
        print('You do not have ffmpeg installed!', e)
        print('You can install ffmpeg by reading https://github.com/kkroening/ffmpeg-python/issues/251')
        return False


def extract_video_config(video_full_path, thumb_full_path, thumb_name):
    """Get configs and thumbnail of the video, by OpenCV."""
    try:
        import cv2
    except ModuleNotFoundError:
        print('You do not have cv2 module, please install by yourself!')
        return None, 0, 640, 360

    cam = cv2.VideoCapture(video_full_path)

    if cam.get(cv2.CAP_PROP_FRAME_COUNT) == 0:
        print('Invalid video detected!')
        return None, 0, 640, 360

    try:
        # duration = frame count / frame per second
        duration = cam.get(cv2.CAP_PROP_FRAME_COUNT) / cam.get(cv2.CAP_PROP_FPS)
    except ZeroDivisionError:
        duration = 0
    width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

    success, image = cam.read()
    if success:
        # DOC: "The thumbnail should be in JPEG format and less than 200 kB in size."
        save_compressed_image(image, thumb_full_path, MAX_THUMB_SIZE)

        return thumb_name, math.ceil(duration), int(width), int(height)
    return None, math.ceil(duration), int(width), int(height)


def detect_and_download_video(url, path, name, verbose):
    """Detect and download videos in page, return video name, by Youtube-DL."""
    try:
        import youtube_dl
    except ModuleNotFoundError:
        print('You do not have youtube-dl, please install by yourself!')
        return None

    # Specific file name, disable logs and warnings as default
    ydl_opts = {'outtmpl': os.path.join(path, name) + '.%(ext)s'}   # .%(ext)s
    if verbose:
        ydl_opts['quiet'] = True
        ydl_opts['no_warnings'] = True
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(url, download=True)
        except Exception:
            return None

    if 'entries' in meta and len(meta['entries']) > 0:
        return name + '.' + meta['entries'][0]['ext']
    elif 'ext' in meta:
        return name + '.' + meta['ext']
        # return name + '.mp4'
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
