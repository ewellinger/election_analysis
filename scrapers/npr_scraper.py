from pymongo import MongoClient
from requests import get
from unidecode import unidecode
from load_data import get_keywords_2016, get_dates
from sys import argv
import threading
import os
# Import NPR API Access key from zsh profile
api_key = os.environ['NPR_ACCESS_KEY']


def single_query(searchterm, date, start_num=0):
    payload = {
        'id': '1014,1003',
        'fields': 'all',
        'requiredAssets': 'text',
        'date': date,
        'searchTerm': searchterm,
        'startNum': start_num,
        'dateType': 'story',
        'output': 'JSON',
        'numResults': 20,
        'searchType': 'fullContent',
        'apiKey': api_key
    }
    url = 'http://api.npr.org/query'
    response = get(url, params=payload)
    if response.status_code != 200:
        print('WARNING', response.status_code)
    else:
        return response.json()


def extract_info(article):
    '''
    INPUT: dict object with output from the api
    OUTPUT: bool if extraction was successful or not,
            dict object to insert into mongodb
    '''
    headline = unidecode(article['title']['$text'])
    date_published = str(article['pubDate']['$text'])
    try:
        author = [str(author['name']['$text']) for author in article['byline']]
    except:
        author = None
    try:
        url = str(article['link'][0]['$text'])
    except:
        return False, ''
    try:
        article_text = unidecode(' '.join([line.get('$text', '\n') for line in article['text']['paragraph']]))
    except:
        return False, ''
    insert = {'url': url,
              'source': 'npr',
              'headline': headline,
              'date_published': date_published,
              'author': author,
              'article_text': article_text}
    return True, insert


def scrape_npr(tab, searchterm, dates, page_num=0):
    articles = []
    num_bad_extractions = 0
    for date in dates:
        response = single_query(searchterm, date)
        if 'message' in response.keys():
            pass
        else:
            for article in response['list']['story']:
                articles.append(article)
    for article in articles:
        insert = extract_info(article)
        if insert[0] and not already_exists(tab, insert[1]['url']):
            tab.insert_one(insert[1])
        if not insert[0]:
            num_bad_extractions += 1
    return num_bad_extractions


def thread_scrape_npr(tab, searchterm, dates):
    self = threading.current_thread()
    self.result = scrape_npr(tab, searchterm, dates)


def already_exists(tab, url):
    return bool(tab.find({'url': url}).count())


def concurrent_scrape_npr(tab, searchterms, dates):
    threads = []
    for searchterm in searchterms:
        thread = threading.Thread(target=thread_scrape_npr,
                                  args=(tab, searchterm, dates))
        threads.append(thread)
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    num_bad_extractions = 0
    for thread in threads:
        num_bad_extractions += thread.result
    return num_bad_extractions


if __name__=='__main__':
    ''' This script should be called in the following way:
    $ python npr_scraper.py 'startdate' 'enddate' 'table (optional)'
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
    print('Scraping NPR from {0} to {1}'.format(start_date, end_date))

    dates = get_dates(start_date, end_date)
    keywords = get_keywords_2016()

    num_bad_extractions = concurrent_scrape_npr(tab, keywords, dates)

    print('NPR Scraping Done...')
    print('Number of Bad Extractions = {0}'.format(num_bad_extractions))
