#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
RSS-feed parser for multiple rss-feeds from URLs.
In development for the E-Paper-Calendar software.
Currently in alpha phase. Beta testers more than welcome. Please send me a mail to let me know what can be fixed/improved here. Thanks.

Copyright by aceisace
"""

import feedparser
import arrow
import datetime

rss_feeds=[
    "http://feeds.bbci.co.uk/news/world/rss.xml#",
    ]

"""How old should the oldest posts be in days?"""
max_range = 14 # 2 weeks


today = datetime.date.today()
time_span = today - datetime.timedelta(days=max_range)

for feeds in rss_feeds:
    parse = feedparser.parse(feeds)
    print(parse['feed']['title'])
    print('________________________')
    for posts in parse.entries:
    # RSS feeds may contain year as '2013' or just '13', hence the 2 options below
        try:
            post_dt = datetime.datetime.strptime(posts.published, '%a, %d %b %Y %H:%M:%S %Z')
        except Exception as e:
            post_dt = datetime.datetime.strptime(posts.published, '%a, %d %b %y %H:%M:%S %Z')
            
        if post_dt.date() >= time_span:
            print(arrow.get(post_dt).humanize(), '\n',posts.title)
            #local.humanize(locale='ko_kr')
