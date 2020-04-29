# -*- coding: UTF-8 -*-
import re

from .utils import (
    is_length_immunity,
)

MAXLEN = 4096


def default_policy(item, max_len=1000, max_par_num=15):
    parse_mode = 'html'
    disable_web_page_preview = 'True'
    # disable_notification = 'Ture'

    max_len = max_len
    max_par_num = max_par_num

    if is_length_immunity(item):
        # full is the full text you want to post
        full = '<b>' + item['title'] + '</b>\n\n' + item['paragraphs'] + item['time'] + '\n' + \
               '[' + item['source'] + ']' + '<a href=\"' + item['link'] + '\">[Full text]</a>' + ' '
        # Remember that even the text is not limited by length, we still ensure its length is under MAXLEN
        max_len = min(len(full), MAXLEN)

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

    assert len(po) < MAXLEN

    return po, parse_mode, disable_web_page_preview


def default_id_policy(self, link):
    return re.findall('\\d+', link)[-1]
