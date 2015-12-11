from pymongo import MongoClient
from load_data import get_keywords_2016, get_week_tuples
from requests import get
from unidecode import unidecode
from bs4 import BeautifulSoup
from time import sleep
import os
# Import NYT API Access key from zsh profile
api_key = os.environ['NYT_ACCESS_KEY']


def single_query(searchterm, date_tup, page=0):
    searchterm = searchterm.replace(' ', '+')
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?q={0}&fq=news_desk%3APolitics&begin_date={1}&end_date={2}&page={3}&api-key={4}'.format(searchterm, date_tup[0], date_tup[1], page, api_key)
    response = get(url)
    # Make sure you don't hit the 10 calls per second limit
    sleep(1.0/10)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    elif response.json()['status'] != 'OK':
        print 'WARNING', response.json()['status']
    else:
        return response.json()


def extract_info(tab, article):
    '''
    INPUT: Mongo table pointer, JSON object from NYT API
    OUTPUT:
        bool on whether extration was successful or not (Will also return False if the url already exists in the Mongo table)
        Dict to insert into Mongo Database
    By checking the Mongo table during the extraction process we can save time by not getting the html of the url if that url already exists in the table.
    '''
    date_published = parse_str(article['pub_date'])
    url = article['web_url']
    source = article['source']
    content_type = article['type_of_material']
    if already_exists(tab, url):
        return False, ''
    html = get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    try:
        author = ['{} {}'.format(person['firstname'], person['lastname']) for person in article['byline']['person']]
    except:
        author = None
    try:
        if content_type == 'Blog':
            lines = soup.find('div', attrs={'class': 'entry-content'}).findAll('p')
        else:
            lines = soup.find('div', attrs={'class': 'story-body'}).findAll('p')
        article_text = parse_str(' \n '.join([line.text for line in lines]))
    except:
        print 'WARNING! Extracting the text got all fucked up!'
        return False, ''
    try:
        headline = parse_str(soup.find('h1', attrs={'itemprop': 'headline', 'class': 'entry-title'}).text)
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
    # num_bad_extractions = 0
    print 'Scraping API for {}...'.format(searchterm)
    for date in dates:
        response = single_query(searchterm, date)
        hits = response['response']['meta']['hits']
        for article in response['response']['docs']:
            articles.append(article)
        if hits > 10:
            for i in xrange(hits / 10):
                response = single_query(searchterm, date, page=i+1)
                for article in response['response']['docs']:
                    articles.append(article)
    print 'Done.'
    print 'Extracting and adding to Mongo...'
    inserts = [extract_info(tab, article) for article in articles]
    for insert in inserts:
        if insert[0] and searchterm in insert[1]['article_text'].lower():
            tab.insert_one(insert[1])
    print 'Done.'
    print '\n'


def already_exists(tab, url):
    return bool(tab.find({'url': url}).count())


def parse_str(x):
    if type(x) == unicode:
        return unidecode(x)
    else:
        return str(x)


if __name__=='__main__':
    # Create MongoClient
    client = MongoClient()
    # Initialize the Database
    db = client['election_analysis']
    # Initialize table
    tab = db['articles']

    keywords = get_keywords_2016()
    dates = get_week_tuples(end_mon=11)
    # Convert dates from YYYY-MM-DD to YYYYMMDD
    dates = [(date[0].replace('-', ''), date[1].replace('-', '')) for date in dates]

    for searchterm in keywords:
        scrape_nyt(tab, searchterm, dates)
