from pymongo import MongoClient
from load_data import get_keywords_2016, get_week_tuples, parse_str
from requests import get
from bs4 import BeautifulSoup
from time import sleep
import os
from sys import argv
# Import NYT API Access key from zsh profile
api_key = os.environ['NYT_ACCESS_KEY']


def single_query(searchterm, date_tup, page=0):
    payload = {
        'q': searchterm,
        'begin_date': date_tup[0],
        'end_date': date_tup[1],
        'page': page,
        'api-key': api_key
    }
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
    response = get(url, params=payload)

    # Make sure you don't hit the 10 calls per second limit
    sleep(1.0 / 10)
    if response.status_code != 200:
        print 'WARNING', response.status_code
        print response.url
    elif response.json()['status'] != 'OK':
        print 'WARNING', response.json()['status']
    else:
        return response.json()


def extract_info(tab, article):
    '''
    INPUT: Mongo table pointer, JSON object from NYT API
    OUTPUT:
        bool on whether extration was successful or not (Will also return False if the url already exists in the Mongo table, if the source is no longer availible on NYTime, or the section is something we don't care about)
        Dict to insert into Mongo Database or empty string if it isn't something we want to insert into Mongo
    By checking the Mongo table during the extraction process we can save time by not getting the html of the url if that url already exists in the table.
    '''
    date_published = parse_str(article['pub_date'])
    url = article['web_url']
    source = article['source']
    content_type = article['type_of_material']
    # Skip extraction if article already exists in Mongo
    if already_exists(tab, url):
        return False, ''
    # Skip these sections as they don't contain any text that we'd be
    # interested in.
    sections_to_skip = ['Video', 'Interactive Feature',
                        'Paid Death Notice', 'Slideshow', 'Question', 'Review']
    # Skip extraction if the source is 'AP' or 'Reuters' as those sources
    # aren't accessable through NYTimes anymore
    if source in ['AP', 'Reuters'] or content_type in sections_to_skip:
        return False, ''
    html = get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    try:
        author = ['{} {}'.format(person['firstname'], person[
                                 'lastname']) for person in article['byline']['person']]
    except:
        author = None
    try:
        if content_type == 'Blog':
            lines = soup.find(
                'div', attrs={'class': 'entry-content'}).findAll('p')
        else:
            lines = soup.find(
                'div', attrs={'class': 'story-body'}).findAll('p')
        article_text = parse_str(' \n '.join([line.text for line in lines]))
    except:
        print 'WARNING! Text Extraction Failed'
        print (url, content_type, source)
        return False, ''
    try:
        headline = parse_str(
            soup.find('h1', attrs={'itemprop': 'headline', 'class': 'entry-title'}).text)
    except:
        headline = parse_str(article['headline']['main'])
    insert = {'url': url,
              'source': 'nyt',
              'content_source': source,
              'content_type': content_type,
              'headline': headline,
              'date_published': date_published,
              'author': author,
              'article_text': article_text}
    return True, insert


def scrape_nyt(tab, searchterm, dates):
    articles = []
    print 'Scraping API for {}...'.format(searchterm)
    for date in dates:
        response = single_query(searchterm, date)
        hits = response['response']['meta']['hits']
        for article in response['response']['docs']:
            articles.append(article)
        if hits > 10:
            for i in xrange(hits / 10):
                response = single_query(searchterm, date, page=i + 1)
                for article in response['response']['docs']:
                    articles.append(article)
    print 'Done.'
    print 'Extracting...'
    inserts = [extract_info(tab, article) for article in articles]
    print 'Adding to Mongo...'
    for insert in inserts:
        if insert[0] and searchterm in insert[1]['article_text'].lower():
            tab.insert_one(insert[1])
    print 'Done.'
    print '\n'


def already_exists(tab, url):
    return bool(tab.find({'url': url}).count())


if __name__ == '__main__':
    ''' This script should be called in the following way:
    $ python nyt_scraper.py 'startdate' 'enddate' 'table (optional)'
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

    keywords = get_keywords_2016()
    start_date, end_date = argv[1], argv[2]
    dates = get_week_tuples(start_date, end_date, strf='%Y%m%d')

    for searchterm in keywords:
        scrape_nyt(tab, searchterm, dates)
