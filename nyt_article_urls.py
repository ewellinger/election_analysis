from load_data import get_keywords_2016, get_week_tuples
from requests import get
import os
# Import NYT API Access key from zsh profile
api_key = os.environ['NYT_ACCESS_KEY']


def single_query(searchterm, date_tup, page=0):
    searchterm = searchterm.replace(' ', '+')
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?q={0}&fq=news_desk%3APolitics&begin_date={1}&end_date={2}&page={3}&api-key={4}'.format(searchterm, date_tup[0], date_tup[1], page, api_key)
    response = get(url)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    elif response.json()['status'] != 'OK':
        print 'WARNING', response.json()['status']
    else:
        return response.json()


if __name__=='__main__':
    keywords = get_keywords_2016()
    dates = get_week_tuples(end_mon=11)
    # Convert dates from YYYY-MM-DD to YYYYMMDD
    dates = [(date[0].replace('-', ''), date[1].replace('-', '')) for date in dates]

    response = single_query('trump', dates[-2])
