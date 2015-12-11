from bs4 import BeautifulSoup
from requests import get
from load_data import get_keywords_2016, get_dates
import json
import os
# Import WSJ Access Credentials from zsh profile
# user_name = os.environ['WSJ_USER_ACCOUNT']
# password = os.environ['WSJ_PASSWORD']


def single_query(date):
    url = 'http://www.wsj.com/public/page/archive-{0}.html'.format(date)
    response = get(url)
    if response.status_code != 200:
        print 'WARNING', response.status_code
        print date
    else:
        return response


def get_urls(date, keywords, urls):
    html = single_query(date)
    try:
        soup = BeautifulSoup(html.content, 'html.parser')
    except:
        return urls

    # This will create a list of Tag elements for each story on the page
    articles = soup.find('ul', attrs={'class': 'newsItem'}).findAll('li')

    for article in articles:
        add_url = False
        for keyword in keywords:
            # Check the title and summary of the article for the presence of each searchterm.  If found, set the add_url flag to add the link to the urls set
            if keyword in article.find('a').text.lower():
                add_url = True
            elif keyword in article.text.lower():
                add_url = True
        if add_url:
            urls.add(article.find('a').get('href'))
    return urls


if __name__=='__main__':
    keywords = get_keywords_2016()
    dates = get_dates(end_mon=11)

    urls = set()

    for date in dates:
        urls = get_urls(date, keywords, urls)

    # Convert urls set to a list and write to a txt file
    with open('./url_files/wsj_article_urls_2016.txt', 'w') as f:
        f.write(json.dumps(list(urls)))
        f.close()
