from pymongo import MongoClient
from bs4 import BeautifulSoup
from requests import get
import json
from unidecode import unidecode
from load_data import load_urls, get_file_name
from sys import argv


def add_to_mongo(tab, url):
    if already_exists(tab, url):
        return False
    try:
        html = get(url)
    except:
        return url

    soup = BeautifulSoup(html.content, 'html.parser')

    try:
        headline = unidecode(soup.find('h1', attrs={'itemprop': 'headline'}).contents[0])
    except:
        return url
    try:
        date_published = soup.find('time', attrs={'itemprop': 'datePublished'}).get('datetime')
    except:
        return url
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
    ''' This script should be called in the following way:
    $ python fox_scraper.py 'startdate' 'enddate' 'table (optional)'
    '''
    # Create MongoClient
    client = MongoClient()
    # Initialize the Database
    db = client['election_analysis']
    # Initialize table
    # If a table name has been provided use that, otherwise initialize 'articles' table
    if len(argv) > 3:
        tab = db[argv[3]]
    else:
        tab = db['articles']

    start_date, end_date = argv[1], argv[2]
    print 'Scraping FOX URLs from {0} to {1}'.format(start_date, end_date)

    file_path = '../url_files/{0}'.format(get_file_name('fox', start_date, end_date))
    urls = load_urls(file_path)

    bad_urls = []
    for url in urls:
        result = add_to_mongo(tab, url)
        if result:
            bad_urls.append(result)

    print 'FOX Scraping Done...'
    print 'Number of Bad Extractions = {0}'.format(bad_urls)
