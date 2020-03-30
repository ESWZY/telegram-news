# -*- coding: UTF-8 -*-
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
)

from displaypolicy import (
    default_policy,
)
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80 Safari/537.36'}
proxies = {  }
TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
channel = os.getenv("CHANNEL")

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

class NewsExtractor(object):
    _ready = False
    _listURLs = []
    _lang = ""
    _sendList = []
    display_policy = default_policy

    def __init__(self, listURLs, sendList = [], lang = '', display_policy = default_policy):
        self.listURLs = listURLs
        self._lang = lang
        self._sendList = sendList
        self.display_policy = display_policy

    def getList(self, listURL):
        res = requests.get(listURL, headers = headers)
        if res.status_code == 200:
            res.encoding='utf-8'
            #print(res.text)

            newsList = []

            soup = BeautifulSoup(res.text,'lxml')
            data = soup.select('.dataList > .clearfix > h3 > a')    # TODO: compatibility
            #print(data)

            for item in data:
                result = {
                    "title": item.get_text(),
                    "link": item.get('href'),
                    'ID': re.findall('\d+',item.get('href'))[-1]
                }
                newsList.append(result)

            return newsList
        else:
            print('List URL error exception!')
            return None

    def getFull(self, url, item):
        res = requests.get(url, headers = headers)
        res.encoding='utf-8'
        #print(res.text)
        time = ''
        source = ''
        title = ''
        
        soup = BeautifulSoup(res.text,'lxml')

        # Get release time and source
        timeSelect = soup.select('.h-info > span:nth-child(1), '# TODO: compatibility
                                 '.time')
        try:
            time = timeSelect[0].getText().strip()
        except IndexError:                              # Do not have this element because of missing/403/others
            time = ""

        sourceSelect = soup.select('.h-info > span:nth-child(2), '# TODO: compatibility
                                   '.source')
        try:
            source = sourceSelect[0].getText().strip().replace('\n','')
        except IndexError:                              # Do not have this element because of missing/403/others
            source = ""

        # Get news title
        titleSelect = soup.select('.h-title, '# TODO: compatibility
                                  '.title, '
                                  '.Btitle')
        try:
            title = titleSelect[0].getText().strip()
        except IndexError:                              # Do not have this element because of missing/403/others
            title = ""

        # Get news body
        # Two select ways:
        # Mobile news page: '.main-article > p'
        # Insatnce news page: '#p-detail > p'
        paragraphSelect = soup.select('p')
        #return paragraphSelect
        #print(paragraphSelect)

        paragraphs = ""
        for p in paragraphSelect:
            linkStr = keep_link(str(p)).strip('\u3000').strip('\n').strip()
            if linkStr != "": 
                paragraphs += linkStr + '\n\n'
        #print(paragraphs)

        return {'title': title, 'time': time, 'source': source, 'paragraphs': paragraphs, 'link': url}

    def post(self, item, news_id):

        # Get display policy by item info
        po, parse_mode, disable_web_page_preview= self.display_policy(item)

        # Must url encode the text
        po = str_url_encode(po)

        res = None
        for channel in self._sendList:
        # https://core.telegram.org/bots/api#sendmessage    
            postURL = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + channel + '&text=' + po + '&parse_mode=' + parse_mode + '&disable_web_page_preview=' + disable_web_page_preview
            res = requests.get(postURL, proxies=proxies)
            if res.status_code == 200:
                db.execute("INSERT INTO news (news_id, time) VALUES (:news_id, NOW())",
                                    {"news_id":news_id})
                # Commit changes to database
                db.commit()
            else:
                print('REEOR! NOT POSTED BECAUSE OF ' + str(res.status_code))
        return res
        
    def isPosted(self, news_id):
        rows = db.execute("SELECT * FROM news WHERE news_id = :news_id",
                                {"news_id": news_id})
        if rows.rowcount == 0:
            return False
        else:
            return True

    def action(self):
        nlist=[]
        for l in self.listURLs:
            nlist += self.getList(l)

        nlist.reverse()
        #print(nlist)

        total = 0
        posted = 0
        for item in nlist:
            if not self.isPosted(item['ID']):
                message = self.getFull(item['link'], item=item)
                #print(message)

                # Post the message by api
                res = self.post(message, item['ID'])
                print(str(item['ID']) + " " + str(res.status_code))
                total += 1
            else:
                posted += 1
                #print(item['ID'] + 'Posted!')
        return total, posted

    def poll(self, time=30):
        def work():
            while (True):
                total, posted = self.action()
                if total + posted == 0:
                    print('Empty list:')
                print(self._lang + str(total) + ' succeeded,' + str(posted) + ' posted.')
                print('Wait ' + str(time) + 's to restart!')
                sleep(time)

        t = threading.Thread(target=work)
        t.start()

class NewsExtractorJSON(NewsExtractor):

    def __init__(self, listURLs, sendList, lang = '', display_policy = default_policy):
        super(NewsExtractorJSON, self).__init__(listURLs, sendList = sendList, lang = lang, display_policy = display_policy)

    def getList(self, listURL):
        res = requests.get(listURL, headers = headers)
        if res.status_code == 200:
            res.encoding='utf-8'
            #print(res.text)

            newsList = []
            listJSON = None
            try:
                listJSON = json.loads(res.text)
            except json.decoder.JSONDecodeError:
                try:
                    listJSON = json.loads(res.text[1:-2])  # Remove brackets and load as json
                except Exception:
                    pass

            for item in listJSON['data']['list']:
                i = {'ID': 0}
                i['ID'] = item['DocID']
                i['link'] = item['LinkUrl']
                i['title'] = item['Title']
                i["PubTime"] = item["PubTime"]
                i["SourceName"] = item["SourceName"]
                i["Author"] = item["Author"]
                newsList.append(i)

            return newsList
        else:
            print('List URL error exception!')
            return None

    def getFull(self, url, item=None):
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        # print(res.text)
        time = ''
        source = ''
        title = ''

        soup = BeautifulSoup(res.text, 'lxml')

        time = item["PubTime"]
        source = item["SourceName"]
        title = item['title']

        # Get news body
        # Two select ways:
        # Mobile news page: '.main-article > p'
        # Insatnce news page: '#p-detail > p'
        paragraphSelect = soup.select('p')
        # return paragraphSelect
        # print(paragraphSelect)

        paragraphs = ""
        for p in paragraphSelect:
            linkStr = keep_link(str(p)).strip('\u3000').strip('\n').strip()
            if linkStr != "":
                paragraphs += linkStr + '\n\n'
        # print(paragraphs)

        return {'title': title, 'time': time, 'source': source, 'paragraphs': paragraphs, 'link': url}

print("DELETED!!")