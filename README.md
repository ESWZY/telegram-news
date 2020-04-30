# Telegram-news

Python program package for automatically fetching and pushing news by Telegram.

## Simple Start

First of all, install telegram_news:
```shell script
pip install telegram_news
```

In a Python file, write:

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from telegram_news.template.common import InfoExtractor, NewsPostman

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
ie.set_list_selector('#MainPage_latest_news_text > ul > li')
ie.set_title_selector('#firstHeading')
ie.set_paragraph_selector('#mw-content-text > div > p:not(p:nth-child(1))')
ie.set_time_selector('#mw-content-text > div > p:nth-child(1) > strong')
ie.set_source_selector('span.sourceTemplate')
ie.max_post_length = 2000

# News postman to manage sending affair
np = NewsPostman(listURLs=[url, ], sendList=[channel, ], db=db, tag=tag)
np.set_bot_token(bot_token)
np.set_extractor(ie)
np.set_table_name(table_name)

# Start to work!
np.poll()
```

Then, you will get messages like this in your channel or group:

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
>[ "[COVID-19 Confirmed Patients](http://119.40.84.187/surveillance/)" - [IEDCR](https://en.wikipedia.org/wiki/IEDCR) ] [[Full text](https://en.wikinews.org/wiki/Bangladesh_reports_five_new_deaths_due_to_COVID-19,_a_daily_highest?dpl_id=2891328)]

## Example

An example channel is [@wikinews_en](https://t.me/s/wikinews_en)