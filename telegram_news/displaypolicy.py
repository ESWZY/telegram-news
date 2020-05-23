# -*- coding: UTF-8 -*-

"""
Display policies and id policies for different situation.

Add new ones when possible.
"""

import re


MAXLEN = 4096


def default_policy(item, max_len=1000, max_par_num=15):
    """
    Generate formatted message from item, the default way.

    :param item: item dict.
    :param max_len: max message length.
    :param max_par_num: max paragraph number.
    :return: formatted forward message, parse mode (HTML or Markdown), disable web page preview flag.
    """
    parse_mode = 'html'
    disable_web_page_preview = 'True'
    # disable_notification = 'Ture'

    max_len = max_len
    max_par_num = max_par_num

    # po is the text we want to post
    po = ""
    if item['title']:
        po += '<b>' + item['title'] + '</b>'
        po += '\n\n'

    if item['paragraphs']:
        if len(item['paragraphs']) > max_len or item['paragraphs'].count('\n') > max_par_num * 2:
            # Leave a hint
            po += '<i>Too long to display.</i>\n\n'
            # If there is exceed the limit, enable web page preview.
            disable_web_page_preview = 'False'
        else:
            po += item['paragraphs']

        if po[-1] != '\n':
            po += '\n'
        if po[-2] != '\n':
            po += '\n'

    if item['time']:
        po += item['time']
        po += '\n'

    if item['source']:
        po += '[' + item['source'] + ']' + ' '

    if item['link']:
        po += '<a href=\"' + item['link'] + '\">[Full text]</a>'

    po = po.replace('<br>', "")

    if len(po) > MAXLEN:
        return "Too long message!\n" + item['id'], parse_mode, disable_web_page_preview

    return po, parse_mode, disable_web_page_preview


def best_effort_display_policy(item, max_len=1000, max_par_num=15, suffix='...'):
    """
    Display as more paragraphs as possible.
    If over max_len, end with suffix.

    :param item: item dict.
    :param max_len: max message length.
    :param max_par_num: max paragraph number.
    :param suffix: used for indicating an omission.
    :return: formatted forward message, parse mode (HTML or Markdown), disable web page preview flag.
    """
    parse_mode = 'html'
    disable_web_page_preview = 'True'

    full = '<b>' + item['title'] + '</b>\n\n' + item['paragraphs'] + item['time'] + '\n' + \
           '[' + item['source'] + ']' + '<a href=\"' + item['link'] + '\">[Full text]</a>' + ' '

    # po is the text we want to post
    po = ""
    if item['title']:
        po += '<b>' + item['title'] + '</b>'
        po += '\n\n'

    if item['paragraphs']:
        if len(full) > max_len:
            max_len -= len(suffix) + 2
            length = len(full) - len(item['paragraphs'])
            ps = item['paragraphs'].split('\n\n')
            for p in ps:
                if length + len(p) > max_len:
                    po += suffix + '\n\n'
                    break
                else:
                    length += len(p)
                    po += p + '\n\n'
        else:
            po += item['paragraphs']

        if po[-1] != '\n':
            po += '\n'
        if po[-2] != '\n':
            po += '\n'

    if item['time']:
        po += item['time']
        po += '\n'

    if item['source']:
        po += '[' + item['source'] + ']' + ' '

    if item['link']:
        po += '<a href=\"' + item['link'] + '\">[Full text]</a>'

    po = po.replace('<br>', "")

    if len(po) > 4096:
        return "Too long message!\n" + item['id'], parse_mode, disable_web_page_preview

    return po, parse_mode, disable_web_page_preview


def default_id_policy(self, link):
    """
    Generate id from link, the default way.

    :param self: InfoExtractor.
    :param link: the link of news.
    :return: id string.
    """
    return re.findall('\\d+', link)[-1]
