from pymongo import MongoClient
from selenium import webdriver
from bs4 import BeautifulSoup


def add_to_mongo(tab, html_str):
    pass


def get_urls_from_search(driver, searchterm, date):
    searchterm = searchterm.replace(' ', '%20')
    url = 'http://www.foxnews.com/search-results/search?q={0}&ss=fn&section.path=fnc/politics&type=story&min_date={1}&max_date={1}&start=0'.format(searchterm, date)

    # Get the html from the site and create a BeautifulSoup object from it
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Get the number of search results.  If greater than 10 we'll need to loop through subsequent pages to get the additional urls
    num_found = int(soup.find('span', attrs = {'ng-bind': 'numFound'}).contents[0])

    if num_found <= 10:
        articles = soup.findAll('div', class_='search-article ng-scope')
        return [str(tag.find('a').get('href')) for tag in articles]
    else:
        urls = []
        num_pages = num_found / 10
        articles = soup.findAll('div', class_='search-article ng-scope')
        for tag in articles:
            urls.append(str(tag.find('a').get('href')))
        for page in xrange(2, 2 + num_pages):
            link = driver.find_element_by_link_text(str(page))
            link.click()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.findAll('div', class_='search-article ng-scope')
            for tag in articles:
                urls.append(str(tag.find('a').get('href')))
        return urls







if __name__=='__main__':
    # # Initialize the mongo client
    # client = MongoClient()
    # # Initialize the database
    # db = client['election_analysis']
    # # Initialize the table
    # tab = db['articles']

    searchterm = 'trump'
    date = '2015-12-01'

    # Create the Firefox driver for selenium
    driver = webdriver.Firefox()

    urls = get_urls_from_search(driver, searchterm, date)

    # driver.get(urls[0])
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
