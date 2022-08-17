import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from server.models import new_headline, Headline, safe_commit  # , db
from server import db


def get_nytimes_and_wsj_headlines():
    nytimes = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    wsj_markets = "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
    wsj_world = "https://feeds.a.dj.com/rss/RSSWorldNews.xml"
    return [parse_rss_feed(feed) for feed in (nytimes, wsj_markets, wsj_world)]


def parse_rss_feed(source: str) -> list:
    """
    Extract needed info from rss feeds
    This should work for most rss feeds, although the pubdate format might differ for some sources
    """
    res = requests.get(source)
    root = ET.fromstring(res.text)
    items = root.findall("./channel/item")
    data = [
        {
            "text": i.find("title").text,
            "url": i.find("link").text,
            "date": parse_nytimes_date(i.find("pubDate").text),
        }
        for i in items
    ]
    return data


def parse_nytimes_date(datestring: str | None) -> datetime | None:
    if datestring:
        return datetime.strptime(datestring, "%a, %d %b %Y %H:%M:%S %z")
    else:
        return None


def send_to_database(source):
    if source.name == "New York Times":
        data = parse_rss_feed(
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
        )
    elif source.name == "Wall Street Journal":
        data = parse_rss_feed(
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
        ) + parse_rss_feed("https://feeds.a.dj.com/rss/RSSWorldNews.xml")
    else:
        return
    for item in data:
        match = Headline.query.filter(Headline.text == item["text"]).first()
        if not match:
            safe_commit(new_headline(**item, source_id=source.id))
