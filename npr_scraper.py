import os
from requests import get
import json
from unidecode import unidecode

# Import NPR API Access key from zsh profile
api_key = os.environ['NPR_ACCESS_KEY']

def single_query(searchterm, date, start_num=0):
    searchterm = searchterm.replace(' ', '%20')
    url = 'http://api.npr.org/query?id=1014,1003&fields=all&requiredAssets=text&date={0}&searchTerm={1}&startNum={2}&dateType=story&output=JSON&numResults=20&searchType=fullContent&apiKey={3}'.format(date, searchterm, start_num, api_key)
    response = get(url)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.json()


def extract_info(article):
    '''
    INPUT: dict object with output from the api
    OUTPUT: dict object to insert into mongodb
    '''
    headline = unidecode(article['title']['$text'])
    date_published = str(article['pubDate']['$text'])
    author = [str(author['name']['$text']) for author in article['byline']]
    url = str(article['link'][0]['$text'])
    article_text = unidecode(' '.join([line.get('$text', '\n') for line in article['text']['paragraph']]))
    insert = {'url': url,
              'source': 'npr',
              'headline': headline,
              'date_published': date_published,
              'author': author,
              'article_text': article_text}
    return insert

def scrape_npr(tab, searchterm, dates):



if __name__=='__main__':
    # Create MongoClient
    client = MongoClient()
    # Initialize the Database
    db = client['election_analysis']
    # Initialize table
    tab = db['articles']


    # articles = [article for article in response['list']['story']]
    scrape_npr(tab, 'trump', ['2015-03-23', '2015-03-24', '2015-03-25'])
