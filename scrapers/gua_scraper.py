from pymongo import MongoClient
from requests import get
from unidecode import unidecode
from load_data import get_week_tuples, get_keywords_2016
import os
from sys import argv
from time import sleep
# Import Guardian API Access key
api_key = os.environ['GUARDIAN_ACCESS_KEY']


def single_query(searchterm, date):
    payload = {
        'q': searchterm,
        'format': 'json',
        'section': 'us-news',
        'from-date': date[0],
        'to-date': date[1],
        'page-size': 200,
        'show-references': 'author',
        'show-blocks': 'body',
        'api-key': api_key
    }
    url = 'http://content.guardianapis.com/search'
    response = get(url, params=payload)
    if response.status_code != 200:
        print 'WARNING', response.status_code
        return False, ''
    else:
        return True, response.json()


def extract_info(article):
    '''
    INPUT: dict object with output from the api
    OUTPUT: bool if extraction was successful or not,
            dict object to insert into mongodb
    '''
    headline = unidecode(article['webTitle'])
    date_published = str(article['webPublicationDate'])
    try:
        author = article['blocks']['body'][0]['createdBy']['firstName'] + ' ' + article['blocks']['body'][0]['createdBy']['lastName']
    except:
        author = None
    try:
        url = str(article['webUrl'])
    except:
        return False, ''
    try:
        article_text = '\n'.join([unidecode(text_block['bodyTextSummary']) for text_block in article['blocks']['body']])
    except:
        return False, ''
    insert = {'url': url,
              'source': 'guardian',
              'headline': headline,
              'date_published': date_published,
              'author': author,
              'article_text': article_text}
    return True, insert


def scrape_guardian(tab, searchterm, dates):
    for date in dates:
        response = single_query(searchterm, date)
        sleep(1.0/12)
        if response[0]:
            response = response[1]
            if response['response']['status'] != 'ok':
                print 'WARNING', response['response']['status']
            elif response['response']['total'] == 200:
                print 'WARNING: MAX RESULTS ACHIEVED!'
                print (searchterm, date)
            elif response['response']['total'] == 0:
                pass
            else:
                articles = [article for article in response['response']['results']]
                inserts = [extract_info(article)[1] for article in articles if extract_info(article)[0]]
                for insert in inserts:
                    if not already_exists(tab, insert['url']) and searchterm in insert['article_text'].lower():
                        tab.insert_one(insert)
        else:
            print (searchterm, date)


def already_exists(tab, url):
    return bool(tab.find({'url': url}).count())


if __name__=='__main__':
    ''' This script should be called in the following way:
    $ python gua_scraper.py 'startdate' 'enddate' 'table (optional)'
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
    print 'Scraping the Guardian from {0} to {1}'.format(start_date, end_date)

    dates = get_week_tuples(start_date, end_date)
    searchterms = get_keywords_2016()

    for searchterm in searchterms:
        print searchterm
        # Guardian doesn't like the ' in o'malley
        if searchterm != "o'malley":
            scrape_guardian(tab, searchterm, dates)
