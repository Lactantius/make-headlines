import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from server.models import new_headline, Headline, safe_commit  # , db
from server import db


def get_nytimes_headlines():
    nytimes = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    res = requests.get(nytimes)
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
    data = get_nytimes_headlines()
    for item in data:
        match = Headline.query.filter(Headline.text == item["text"]).first()
        if not match:
            # print(item)
            safe_commit(new_headline(**item, source_id=source.id))
