from pymongo import MongoClient
from requests import get
from unidecode import unidecode
from load_data import get_week_tuples, get_keywords_2016
import os
from time import sleep

# Import Guardian API Access key
api_key = os.environ['GUARDIAN_ACCESS_KEY']


def single_query(searchterm, date):
    searchterm = searchterm.replace(' ', '%20')
    url = 'http://content.guardianapis.com/search?q={0}&format=json&section=us-news&from-date={1}&to-date={2}&page-size=200&show-references=author&show-blocks=body&api-key={3}'.format(searchterm, date[0], date[1], api_key)
    response = get(url)
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
    # Create MongoClient
    client = MongoClient()
    # Initialize the Database
    db = client['election_analysis']
    # Initialize table
    tab = db['articles']

    dates = get_week_tuples(end_mon=11)
    searchterms = get_keywords_2016()

    for searchterm in searchterms:
        print searchterm
        # Guardian doesn't like the ' in o'malley
        if searchterm != "o'malley":
            scrape_guardian(tab, searchterm, dates)
