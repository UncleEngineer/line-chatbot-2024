import feedparser, datetime
import os
import songline

token = os.environ.get('rss-noti-token')
messenger = songline.Sendline(token)

RSS_URLS_FILE = "rss_urls.txt"
LAST_CHECKED_FILE = "last_checked.txt"
def get_rss_urls():
    # Read rss from txt file
    with open(RSS_URLS_FILE, "r") as file:
        return [url.strip() for url in file.readlines()]
        

def get_last_checked_date():
    if os.path.exists(LAST_CHECKED_FILE):
        with open(LAST_CHECKED_FILE, "r") as file:
            return datetime.datetime.fromisoformat(file.read().strip())
    return datetime.datetime.min


def save_last_checked_date(date):
    with open(LAST_CHECKED_FILE, "w") as file:
        file.write(date.isoformat())

def check_rss_feeds():
    rss_urls = get_rss_urls()
    last_checked = get_last_checked_date()
    last_date = last_checked
    # print(last_date)
    
    for rss_url in rss_urls:
        print(f"Checking feed: {rss_url}")
        feed = feedparser.parse(rss_url)

        new_entries = []

        for entry in feed.entries:
            published = datetime.datetime.fromtimestamp(datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").timestamp())        
            
            if published > last_checked:
                new_entries.append(entry.link)

                if published > last_date:
                    last_date = published
        if new_entries:
            print("New entries found")

            for url in new_entries:
                print(url)
                messenger.sendtext(url)
        else:
            print("no new entries found")
    
    if last_date > last_checked:
        save_last_checked_date(last_date)
            


if __name__ == "__main__":
    check_rss_feeds()
    # get_rss_urls()
    # get_last_checked_date()