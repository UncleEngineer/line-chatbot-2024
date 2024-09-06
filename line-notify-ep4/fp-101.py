#feed parser basic 101
import feedparser
url = "https://hnrss.org/frontpage"
feed = feedparser.parse(url)
# print(feed)
# print(type(feed))
# print(feed.keys())
# print(feed['feed'])
# print(feed.entries[0].title)

for entry in feed.entries:
    print(entry.title)
    print(entry.published)

