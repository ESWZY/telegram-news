# -*- coding: UTF-8 -*-
import traceback

import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import threading

from utils import (
    keep_link,
    str_url_encode,
    is_single_media,
    get_full_link,
)

from displaypolicy import (
    default_policy,
    default_id_policy,
)


class InfoExtractor(object):
    _listURLs = []
    _lang = ""
    _sendList = []
    _id_policy = default_id_policy

    _list_selector = '.dataList > .clearfix > h3 > a, ' \
                     '.newsList2 > h2 > a, ' \
                     '.newsList > h2 > a'

    _time_selector = '.h-info > span:nth-child(1), ' \
                     '.time'

    _title_selector = '.h-title, ' \
                      '#conTit > h1, ' \
                      '.title, ' \
                      '.Btitle'

    _source_selector = '.h-info > span:nth-child(2), ' \
                       '.source'

    _paragraph_selector = 'p'

    def __init__(self, sendList=[], lang=''):
        self._DEBUG = True
        self._lang = lang
        self._sendList = sendList

    def set_list_selector(self, list_selector):
        self._list_selector = list_selector

    def set_time_selector(self, time_selector):
        self._time_selector = time_selector

    def set_title_selector(self, title_selector):
        self._title_selector = title_selector

    def set_source_selector(self, source_selector):
        self._source_selector = source_selector

    def set_paragraph_selector(self, paragraph_selector):
        self._paragraph_selector = paragraph_selector

    def set_id_policy(self, id_policy):
        self._id_policy = id_policy

    def get_items_policy(self, text, listURL):
        """Get all items in the list webpage"""
        soup = BeautifulSoup(text, 'lxml')
        data = soup.select(self._list_selector)
        # print(data)

        news_list = []
        for item in data:
            link = get_full_link(item.get('href'), listURL)

            result = {
                "title": item.get_text(),
                "link": link,
                'ID': self._id_policy(link)
            }
            news_list.append(result)
        return news_list

    def get_title_policy(self, text, item):
        """Get news title"""
        soup = BeautifulSoup(text, 'lxml')
        title_select = soup.select(self._title_selector)
        try:
            return title_select[0].getText().strip()
        except IndexError:  # Do not have this element because of missing/403/others
            # But the list have a title
            return item['title']

    def get_paragraphs_policy(self, text, item):
        """Get news body"""
        soup = BeautifulSoup(text, 'lxml')
        paragraph_select = soup.select(self._paragraph_selector)
        # print(paragraph_select)

        url = item['link']
        paragraphs = ""
        blank_flag = False
        for p in paragraph_select:
            link_str = keep_link(str(p), url).strip('\u3000').strip('\n').strip()

            # If there is only ONE [Media] link, it should be concerned as a word.
            # This is the
            if link_str != "" and not is_single_media(link_str):
                if blank_flag:
                    link_str = '\n\n' + link_str
                    blank_flag = False
                paragraphs += link_str + '\n\n'
            elif link_str != "":
                paragraphs += link_str + ' '
                blank_flag = True
        if paragraphs and paragraphs[-1] == ' ':
            paragraphs += '\n\n'
        # print(paragraphs)

        return paragraphs

    def get_time_policy(self, text, item):
        """Get news release time"""
        soup = BeautifulSoup(text, 'lxml')
        time_select = soup.select(self._time_selector)
        try:
            time = ''
            for text in time_select:
                time = text.getText().strip()
                time = time.split('丨')[0]
                if time:
                    break
            time = time.split('\n')[0]
            time = time.split('	')[0]
            #print(time)

            # If time is too long, maybe get irrelevant  info
            if len(time) > 100:
                time = ''
        except IndexError:  # Do not have this element because of missing/403/others
            time = ""
        return time

    def get_source_policy(self, text, item):

        soup = BeautifulSoup(text, 'lxml')
        source_select = soup.select(self._source_selector)
        url = item['link']
        try:
            # Maybe source is a link
            source = keep_link(source_select[0].getText(), url).strip().replace('\n', '')
        except IndexError:  # Do not have this element because of missing/403/others
            source = ""
        return source


class NewsPostman(object):
    _listURLs = []
    _lang = ""
    _sendList = []
    _headers = {}
    _proxies = {}
    _display_policy = default_policy
    _TOKEN = os.getenv("TOKEN")
    _DATABASE_URL = os.getenv("DATABASE_URL")
    _db = scoped_session(sessionmaker(bind=create_engine(_DATABASE_URL)))
    _table_name = 'news'
    _extractor = InfoExtractor()

    # Cache the list webpage and check if modified
    _cache_list = None

    def __init__(self, listURLs, sendList=[], lang='', headers=None, proxies={}, display_policy=default_policy):
        self._DEBUG = True
        self._listURLs = listURLs
        self._lang = lang
        self._sendList = sendList
        self._display_policy = display_policy

        if headers:
            self._headers = headers
        else:
            self._headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/80 Safari/537.36'}
        self._proxies = proxies

    def set_bot_token(self, new_token):
        self._TOKEN = new_token

    def set_database_url(self, new_db_url):
        self._DATABASE_URL = new_db_url
        self._db = scoped_session(sessionmaker(bind=create_engine(self._DATABASE_URL)))

    def set_table_name(self, table_name):
        self._table_name = table_name

    def set_extractor(self, extractor):
        self._extractor = extractor

    def get_list(self, listURL):
        res = requests.get(listURL, headers=self._headers)
        # print(res.text)
        if res.status_code == 200:
            res.encoding = 'utf-8'
            # print(res.text)

            if res.text == self._cache_list:
                print('List not Modified')
                return None
            else:
                self._cache_list = res.text

            return self._extractor.get_items_policy(res.text, listURL)
        else:
            print('List URL error exception! ' + str(res.status_code))
            if res.status_code == 403:
                print('May be your header did not work.')
            return []

    def get_full(self, url, item):
        res = requests.get(url, headers=self._headers)
        res.encoding = 'utf-8'
        # print(res.text)

        title = self._extractor.get_title_policy(res.text, item)
        paragraphs = self._extractor.get_paragraphs_policy(res.text, item)
        time = self._extractor.get_time_policy(res.text, item)
        source = self._extractor.get_source_policy(res.text, item)

        return {'title': title, 'time': time, 'source': source, 'paragraphs': paragraphs, 'link': url}

    def post(self, item, news_id):

        # Get display policy by item info
        po, parse_mode, disable_web_page_preview = self._display_policy(item)

        # Must url encode the text
        if self._DEBUG:
            po += ' DEBGU #D' + str(news_id)
        po = str_url_encode(po)

        res = None
        for chat_id in self._sendList:
            # https://core.telegram.org/bots/api#sendmessage
            post_url = 'https://api.telegram.org/bot' + self._TOKEN + '/sendMessage?chat_id=' + chat_id + '&text=' + po + '&parse_mode=' + parse_mode + '&disable_web_page_preview=' + disable_web_page_preview
            res = requests.get(post_url, proxies=self._proxies)
            if res.status_code == 200:
                self._db.execute("INSERT INTO " + self._table_name + " (news_id, time) VALUES (:news_id, NOW())",
                                 {"news_id": news_id})
                # Commit changes to database
                self._db.commit()
            else:
                print('ERROR! NOT POSTED BECAUSE OF ' + str(res.status_code))
                print(res.text)
                res_time = json.loads(res.text)['parameters']['retry_after']
                sleep(res_time)
        return res

    def is_posted(self, news_id):
        rows = self._db.execute("SELECT * FROM " + self._table_name + " WHERE news_id = :news_id",
                                {"news_id": news_id})
        if rows.rowcount == 0:
            return False
        else:
            return True

    def action(self):
        nlist = []
        for link in self._listURLs:
            l = self.get_list(link)
            if l:
                nlist += l

        if not nlist:
            return None, None

        nlist.reverse()
        # print(nlist)

        total = 0
        posted = 0
        for item in nlist:
            if not self.is_posted(item['ID']):
                message = self.get_full(item['link'], item=item)
                # print(message)

                # Post the message by api
                res = self.post(message, item['ID'])
                print(str(item['ID']) + " " + str(res.status_code))
                total += 1
            else:
                posted += 1
                # print(item['ID'] + 'Posted!')
        return total, posted

    # TODO: If the time is short, we can shorten the news list
    #  or cache the list to reduce database access
    def poll(self, time=30):
        def work():
            while (True):
                try:
                    total, posted = self.action()
                    if total == None:
                        print(self._lang + ':' + ' ' * (6 - len(self._lang)) + '\tList not modified!', end=' ')
                        print('Wait ' + str(time) + 's to restart!')
                        sleep(time)
                        continue
                    print(self._lang + ':' + ' '*(6-len(self._lang)) + '\t' + str(total) + ' succeeded,' + str(posted) + ' posted.', end=' ')
                    print('Wait ' + str(time) + 's to restart!')
                    sleep(time)
                except Exception:
                    traceback.print_exc()
                    sleep(1)

        t = threading.Thread(target=work)
        t.start()


class NewsPostmanJSON(NewsPostman):

    def __init__(self, listURLs, sendList, lang='', display_policy=default_policy):
        super(NewsPostmanJSON, self).__init__(listURLs, sendList=sendList, lang=lang, display_policy=display_policy)

    def get_list(self, listURL):
        res = requests.get(listURL, headers=self._headers)
        if res.status_code == 200:
            res.encoding = 'utf-8'
            # print(res.text)

            newsList = []
            list_json = None
            try:
                list_json = json.loads(res.text)
            except json.decoder.JSONDecodeError:
                try:
                    list_json = json.loads(res.text[1:-2])  # Remove brackets and load as json
                except Exception:
                    pass

            for item in list_json['data']['list']:
                i = {'ID': item['DocID'],
                     'link': item['LinkUrl'],
                     'title': item['Title'],
                     "PubTime": item["PubTime"],
                     "SourceName": item["SourceName"],
                     "Author": item["Author"]}
                newsList.append(i)

            return newsList
        else:
            print('List URL error exception!')
            return None

    def get_full(self, url, item=None):
        res = requests.get(url, headers=self._headers)
        res.encoding = 'utf-8'
        # print(res.text)

        title = item['title']
        paragraphs = self._extractor.get_paragraphs_policy(res.text, item)
        time = item["PubTime"]
        source = item["SourceName"]

        return {'title': title, 'time': time, 'source': source, 'paragraphs': paragraphs, 'link': url}


print("DELETED!!")