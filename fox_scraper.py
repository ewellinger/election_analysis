from pymongo import MongoClient
from bs4 import BeautifulSoup
from requests import get
import json
from unidecode import unidecode
from load_data import load_urls


def add_to_mongo(tab, url):
    if already_exists(tab, url):
        return False
    try:
        html = get(url)
    except:
        return url

    soup = BeautifulSoup(html.content, 'html.parser')
    headline = unidecode(soup.find('h1', attrs={'itemprop': 'headline'}).contents[0])
    date_published = soup.find('time', attrs={'itemprop': 'datePublished'}).get('datetime')
    try:
        author = soup.find('a', attrs={'rel': 'author'}).text
    except:
        author = None
    try:
        article_text = unidecode(soup.find('div', attrs={'class': 'article-text'}).text)
    except:
        return url

    insert = {'url': url,
              'source': 'foxnews',
              'headline': headline,
              'date_published': date_published,
              'author': author,
              'article_text': article_text}
    tab.insert_one(insert)
    return False


def already_exists(tab, url):
    return bool(tab.find({'url': url}).count())


if __name__=='__main__':
    # Create MongoClient
    client = MongoClient()
    # Initialize the Database
    db = client['election_analysis']
    # Initialize table
    tab = db['articles']

    urls = load_urls('./url_files/fox_article_urls_2016.txt')

    bad_urls = []
    for url in urls:
        result = add_to_mongo(tab, url)
        if result:
            bad_urls.append(result)
