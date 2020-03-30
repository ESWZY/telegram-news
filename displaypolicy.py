# -*- coding: UTF-8 -*-
import re

MAXLEN = 4096


def default_policy(item):
    parse_mode = 'html'
    disable_web_page_preview = 'True'
    # disable_notification = 'Ture'

    maxlen = 1000
    maxpar = 10
    po = ""
    po = '<b>' + item['title'] + '</b>'
    po += '\n\n'

    if len(item['paragraphs']) > maxlen or item['paragraphs'].count('\n') > maxpar * 2:
        # Post the link only.
        po += '<a href=\"' + item['link'] + '\">Full text link</a>\n\n'
        # If there is exceed the limit, enable web page preview.
        disable_web_page_preview = 'False'
    else:
        po += item['paragraphs']

    po += item['time']
    po += '\n'
    po += item['source']

    assert len(po) < MAXLEN

    return po, parse_mode, disable_web_page_preview


def default_id_policy(self, link):
    return re.findall('\d+', link)[-1]
