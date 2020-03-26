# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import time
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80 Safari/537.36'}
proxies = {  }
TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
channel = os.getenv("CHANNEL")
jsxwURL = "http://www.xinhuanet.com/jsxw.htm"

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

def getList():
    res = requests.get(jsxwURL, headers = headers)
    res.encoding='utf-8'
    #print(res.text)
    
    soup = BeautifulSoup(res.text,'lxml')
    data = soup.select('.dataList > .clearfix > h3 > a')
    #print(data)

    newsList = []
    for item in data:
        result = {
            "title": item.get_text(),
            "link": item.get('href'),
            'ID': re.findall('\d+',item.get('href'))[-1]
        }
        newsList.append(result)

    return newsList

def getFull(url):
    res = requests.get(url, headers = headers)
    res.encoding='utf-8'
    #print(res.text)
    soup = BeautifulSoup(res.text,'lxml')

    # Get release time and source
    infoSelect = soup.select('.h-info > span')
    try:
        time = infoSelect[0].getText().strip()
    except IndexError:                              # Do not have this element because of missing/403/others
        time = ""
    try:
        source = infoSelect[1].getText().strip().replace('\n','')
    except IndexError:                              # Do not have this element because of missing/403/others
        source = ""
    
    # Get news title
    titleSelect = soup.select('.h-title')
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

    def findLink(p):
        '''Remove tags except <a></a>'''
        if p.select('a') == []:
            return p.getText()
        else:
            cp = str(p)
            result = ""
            for link in p.select('a'):
                other = str(cp).split(str(link))
                
                content = link.get_text()
                url = link.get('href')

                result += BeautifulSoup(other[0],'lxml').getText() + '<a href=\"'+url+'\" >'+content+'</a>'
                cp = str(p).replace(str(other[0])+str(link),"")
            return result + BeautifulSoup(cp, 'lxml').getText()
        
    paragraphs = ""
    for p in paragraphSelect:        
        paragraphs += findLink(p).strip('\u3000').strip('\n') + '\n\n'
    #print(paragraphs)

    return {'title': title, 'time': time, 'source': source, 'paragraphs': paragraphs}

def post(item, channel, news_id):
    po = ""
    po = '<b>' + item['title'] + '</b>'
    po += '\n\n'
    po += item['paragraphs']
    po += item['time']
    po += '\n'
    po += item['source']

    if len(po) > 4050:
        return 'Too long! Use Telegraph!'
    
    # https://core.telegram.org/bots/api#sendmessage    
    postURL = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + channel + '&text=' + po + '&parse_mode=html'
    res = requests.get(postURL, proxies=proxies)
    if res.status_code == 200:
        db.execute("INSERT INTO news (news_id, time) VALUES (:news_id, NOW())",
                            {"news_id":news_id})

        # Commit changes to database
        db.commit()
    return json.dumps(res.text)['ok']
    
def isPosted(news_id):
    rows = db.execute("SELECT * FROM news WHERE news_id = :news_id",
                            {"news_id": news_id})
    if rows.rowcount == 0:
        return False
    else:
        return True

def action():
    nlist = getList()
    nlist.reverse()
    for item in nlist:
        if not isPosted(item['ID']):
            message = getFull(item['link'])
            res = post(message, channel, item['ID'])
            print(item['ID'] + res)
        else:
            print(item['ID'] + 'Posted!')

def poll(time=300):
    while(True):
        time.sleep(time)
        action()

action()
