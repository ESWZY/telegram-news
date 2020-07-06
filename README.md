<h1 align="center">
  <img src="/docs/banner.png" alt="Telegram-news">
  <br>Telegram-news<br>
</h1>

<div align="center">

Python package for automatically fetching and pushing news by Telegram.

[![PyPI](https://img.shields.io/pypi/v/telegram-news)](https://pypi.org/project/telegram-news/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telegram-news?logo=python)
[![License](https://img.shields.io/github/license/ESWZY/telegram-news)](https://github.com/ESWZY/telegram-news/blob/master/LICENSE)
![PyPI - Downloads](https://img.shields.io/pypi/dd/telegram-news)

[![Build Status](https://img.shields.io/travis/ESWZY/telegram-news/master?logo=travis)](https://travis-ci.org/ESWZY/telegram-news)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/3c07fed525da42e89dd3d0376457b4d2)](https://app.codacy.com/manual/ESWZY/telegram-news?utm_source=github.com&utm_medium=referral&utm_content=ESWZY/telegram-news&utm_campaign=Badge_Grade_Dashboard)
[![https://t.me/eswzy](https://img.shields.io/badge/Telegram-ESWZY-blue.svg?logo=telegram)](https://t.me/eswzy)

</div>

## Introduction

This is a easy-to-learn, flexible and standardized message fetching and pushing framework, especially for [Telegram](http://www.telegram.org) and [Telegram Bot](https://core.telegram.org/bots).

The target news source can be HTML page, JSON and XML. We also provide customized process for unknown data format.

Push the latest news to your channel or group once it happens!

## Install

```shell
$ pip install telegram-news
```

Or, you can install by cloning this repository:

```shell
$ git clone https://github.com/ESWZY/telegram-news.git
$ cd telegram-news
$ python setup.py install
```

## Prepare

It does not need much so that you can run your code anywhere.

First, I assume you have a [Telegram account](https://web.telegram.org/#/login). Then, ask [@BotFather](https://t.me/botfather) for a bot and bot token. After that, create a public [channel](https://telegram.org/tour/channels) or [group](https://telegram.org/tour/groups), and remember chat id you just named.

You also need a SQL database. Any SQL database is OK. Especially, I recommend [PostgreSQL](https://www.postgresql.org/).

## Usage

### Basic Example

#### Code

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from telegram_news.template import InfoExtractor, NewsPostman

# Three required fields:
# Your bot token gotten from @BotFather
bot_token = os.getenv("TOKEN")
# Add your bots into a channel as administrators
channel = os.getenv("CHANNEL")
# Your database to store old messages.
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a database session
engine = create_engine(DATABASE_URL)
db = Session(bind=engine.connect())

# The news source
url = "https://en.wikinews.org/wiki/Main_Page"
tag = "Wiki News"
table_name = "wikinews"

# Info extractor to process data format
ie = InfoExtractor()

# Select select element by CSS-based selector
ie.set_list_selector('#MainPage_latest_news_text > ul > li')
ie.set_title_selector('#firstHeading')
ie.set_paragraph_selector('#mw-content-text > div > p:not(p:nth-child(1))')
ie.set_time_selector('#mw-content-text > div > p:nth-child(1) > strong')
ie.set_source_selector('span.sourceTemplate')

# Set a max length for post, Max is 4096
ie.max_post_length = 2000

# News postman to manage sending affair
np = NewsPostman(listURLs=[url, ], sendList=[channel, ], db=db, tag=tag)
np.set_bot_token(bot_token)
np.set_extractor(ie)
np.set_table_name(table_name)

# Start to work!
np.poll()
```

#### Result example

><b>Bangladesh reports five new deaths due to COVID-19, a daily highest</b>
>
>Yesterday, [Bangladesh](https://en.wikinews.org/wiki/Bangladesh) has confirmed five new deaths due to [COVID-19](https://en.wikinews.org/wiki/COVID-19) on the day. This is the highest number of fatalities in a day due to the virus. As of yesterday, Bangladesh's [Institute of Epidemiology, Disease Control and Research](https://en.wikipedia.org/wiki/Institute_of_Epidemiology,_Disease_Control_and_Research) (IEDCR) reported the number of recorded infected cases included 114 active cases and 33 recovered cases who were staying home. A total of 17 deaths have been recorded.
>
>In an online news briefing, the director of IEDCR, Dr [Meerjady Sabrina Flora](https://en.wikipedia.org/wiki/Meerjady_Sabrina_Flora)
>
>A hospital official told Anadolu Agency, a local news outlet, that one of the deceased was Jalal Saifur Rahman, a director of Bengali Anti-Corruption Commission, who was cared for at the Kuwait Maitree Hospital.
>
>On Saturday, in an online video announcement, Bangladeshi Road Transport and Bridges Minister Obaidul Quader said public transport would be shut down for longer than initially planned, until this coming Saturday. This public transport shutdown had initially started on March 26 and was planned to end on Saturday, April 4. Transport of essential goods -- medical, fuel and food -- was still allowed.
>
>The first recorded incidents of COVID-19 infection in Bangladesh were on March 8, in two people who returned from Italy and also the wife of one of them. As of March 19, these three had already recovered.
>
>Wednesday, April 8, 2020
>
>[ "[COVID-19 Confirmed Patients](http://119.40.84.187/surveillance/)" - [IEDCR](https://en.wikipedia.org/wiki/IEDCR) ] [[Full Text](https://en.wikinews.org/wiki/Bangladesh_reports_five_new_deaths_due_to_COVID-19,_a_daily_highest?dpl_id=2891328)]

#### Example Channel

An example channel is [@wikinews_en](https://t.me/s/wikinews_en)

### Advanced Example

```python
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from telegram_news.template import InfoExtractor, NewsPostman
    bot_token = os.getenv("TOKEN")
    channel = os.getenv("CHANNEL")
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    db = Session(bind=engine.connect())

    # Above code is as same as the basic example, you can reuse those code directly

    url_2 = "https://www.cnbeta.com/"
    tag_2 = "cnBeta"
    table_name_2 = "cnbetanews"
    
    ie_2 = InfoExtractor()
    ie_2.set_list_selector('.items-area > div > dl > dt > a')
    ie_2.set_title_selector('header > h1')
    
    # Select many target at same time    
    ie_2.set_paragraph_selector('div.cnbeta-article-body > div.article-summary > p, '  # Summary only
                                'div.cnbeta-article-body > div.article-content > p')   # Content only
    ie_2.set_time_selector('header > div > span:nth-child(1)')
    ie_2.set_source_selector('header > div > span.source')
    
    # Select image to display, then the max length is down to 1024
    ie_2.set_image_selector('div.cnbeta-article-body > div.article-summary > p img, '  # From summary only
                            'div.cnbeta-article-body > div.article-content > p img')   # From content only
    ie_2.max_post_length = 1000

    np_2 = NewsPostman(listURLs=[url_2, ], sendList=[channel], tag=tag_2, db=db)
    np_2.set_extractor(ie_2)
    np_2.set_table_name(table_name_2)
    np_2.poll()
```

### Advanced Example for JSON and XML

The handle for JSON and XML are quite similar. You can convert XML to JSON by function `telegram_news.utils.xml_to_json`, and use `NewsPostmanJSON` and `InfoExtractorJSON`. Or, you can use `NewsPostmanXML` and `InfoExtractorXML` directly.

You should use key list to recursively route to the information you want.

```python
    url_3 = "https://www.scmp.com/rss/91/feed"
    tag_3 = "SCMP"
    table_name_3 = "scmpnews"
    
    ie_3 = InfoExtractorJSON()
    
    # Pre-process the XML string, convert to JSON string
    def list_pre_process(text):
        text = json.loads(xml_to_json(text))
        return json.dumps(text)
    ie_3.set_list_pre_process_policy(list_pre_process)
    
    # Route by key list
    ie_3.set_list_router(['rss', 'channel', 'item'])
    ie_3.set_link_router(['link'])
    ie_3.set_title_router(['title'])
    ie_3.set_paragraphs_router(['description'])
    ie_3.set_time_router(['pubDate'])
    ie_3.set_source_router(['author'])
    ie_3.set_image_router(['media:thumbnail', '@url'])
    
    # Customize ID for news item
    def id_policy(link):
        return hashlib.md5(link.encode("utf-8")).hexdigest()
    ie_3.set_id_policy(id_policy)
    
    np_3 = NewsPostmanJSON(listURLs=[url_3], sendList=[channel], db=db, tag=tag_3)
    np_3.set_extractor(ie_3)
    np_3.set_table_name(table_name_3)
    np_3.poll()
```

## Feedback

Feel free to contact with me if you have any question. Also welcome any contribute.

## License

Licensed under the MIT License.
