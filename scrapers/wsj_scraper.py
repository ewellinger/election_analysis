from bs4 import BeautifulSoup
from selenium import webdriver
from load_data import load_urls, parse_str, get_file_name
from pymongo import MongoClient
import os
import json
from time import sleep
from sys import argv
import requests
# Import WSJ Access Credentials from zsh profile
USER_NAME = os.environ['WSJ_USER_ACCOUNT']
PASSWORD = os.environ['WSJ_PASSWORD']


def log_in_wsj():
    url = 'https://id.wsj.com/access/pages/wsj/us/signin.html?url=http%3A%2F%2Fwww.wsj.com&mg=id-wsj'
    driver = webdriver.Firefox()
    driver.get(url)

    user = driver.find_element_by_name('username')
    user.click()
    user.send_keys(USER_NAME)

    pwrd = driver.find_element_by_name('password')
    pwrd.click()
    pwrd.send_keys(PASSWORD)

    driver.find_element_by_id('submitButton').click()
    sleep(10)
    return driver


def extract_info(tab, driver, url):
    if already_exists(tab, url):
        return False, 'already exists'

    # Get the html from the site and create a BeautifulSoup object from it
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        headline = parse_str(soup.find('h1', attrs={'class': 'wsj-article-headline', 'itemprop': 'headline'}).text)
    except:
        print 'WARNING: Error extracting headline'
        return False, ''

    if headline == 'Corrections & Amplifications':
        return False, ''

    try:
        date_published = soup.find('time', attrs={'class': 'timestamp'}).text.replace('\n', '').replace('Updated', '').strip()
    except:
        print 'WARNING: Error extracting date_published'
        print url
        return False, ''
    try:
        author = soup.find('span', attrs={'class': 'name', 'itemprop': 'name'}).text
    except:
        author = None
    try:
        tag = soup.find('div', attrs={'id': 'wsj-article-wrap', 'itemprop': 'articleBody'}).findAll('p')
        article_text = parse_str(' \n '.join([line.text for line in tag]))
    except:
        print 'WARNING: Error extracting article text'
        print url
        return False, ''

    insert = {'url': url,
              'source': 'wsj',
              'headline': headline,
              'date_published': date_published,
              'author': author,
              'article_text': article_text}
    return True, insert


def scrape_wsj(tab, driver, urls, good_urls, bad_urls):
    inserts = []
    for url in urls:
        response = extract_info(tab, driver, url)
        if response[0]:
            good_urls.append(url)
            inserts.append(response[1])
            tab.insert_one(response[1])
        elif response[1] == 'already exists':
            good_urls.append(url)
            pass
        else:
            bad_urls.append(url)
    return inserts, good_urls, bad_urls


def already_exists(tab, url):
    return bool(tab.find({'url': url}).count())


if __name__=='__main__':
    ''' This script should be called in the following way:
    $ python wsj_scraper.py 'startdate' 'enddate' 'table (optional)'
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
    print 'Scraping WSJ URLs from {0} to {1}'.format(start_date, end_date)

    file_path = '../url_files/{0}'.format(get_file_name('wsj', start_date, end_date))
    urls = load_urls(file_path)
    good_urls, bad_urls = [], []

    driver = log_in_wsj()

    inserts, good_urls, bad_urls = scrape_wsj(tab, driver, urls, good_urls, bad_urls)
    driver.close()

    print 'WSJ Scraping Done...'
    print 'Number of Bad URLs = {0}'.format(len(bad_urls))
    if len(bad_urls):
        file_path = '../url_files/{0}'.format(get_file_name('wsj', start_date, end_date, bad=True))
        with open(file_path, 'w') as f:
            f.write(json.dumps(list(bad_urls)))
            f.close()
