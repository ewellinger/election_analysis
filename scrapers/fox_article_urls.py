from selenium import webdriver
from bs4 import BeautifulSoup
import json
import threading
from load_data import get_keywords_2016, get_week_tuples, get_file_name
from sys import argv


def get_urls_from_search(driver, searchterm, date, attempt=0):
    searchterm = searchterm.replace(' ', '%20')
    url = 'http://www.foxnews.com/search-results/search?q={0}&ss=fn&section.path=fnc/politics&type=story&min_date={1}&max_date={2}&start=0'.format(searchterm, date[0], date[1])

    # Get the html from the site and create a BeautifulSoup object from it
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        # Get the number of search results.  If greater than 10 we'll need to
        # loop through subsequent pages to get the additional urls
        num_found = int(
            soup.find('span', attrs={'ng-bind': 'numFound'}).contents[0])

        if num_found <= 10:
            articles = soup.findAll('div', class_='search-article ng-scope')
            return True, [str(tag.find('a').get('href')) for tag in articles]
        else:
            urls = []
            num_pages = num_found / 10
            articles = soup.findAll('div', class_='search-article ng-scope')
            for tag in articles:
                urls.append(str(tag.find('a').get('href')))
            if num_found % 10 == 0:
                for page in xrange(2, 1 + num_pages):
                    link = driver.find_element_by_link_text(str(page))
                    link.click()
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    articles = soup.findAll(
                        'div', class_='search-article ng-scope')
                    for tag in articles:
                        urls.append(str(tag.find('a').get('href')))
            else:
                for page in xrange(2, 2 + num_pages):
                    link = driver.find_element_by_link_text(str(page))
                    link.click()
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    articles = soup.findAll(
                        'div', class_='search-article ng-scope')
                    for tag in articles:
                        urls.append(str(tag.find('a').get('href')))
            return True, urls
    except:
        if attempt < 3:
            attempt += 1
            return get_urls_from_search(driver, searchterm, date, attempt)
        else:
            return False, url


def get_urls(driver, searchterm, dates, good_urls, bad_searches):
    for date in dates:
        response = get_urls_from_search(driver, searchterm, date)
        if response[0]:
            for url in response[1]:
                good_urls.add(url)
        else:
            bad_searches.add((searchterm, date))
    return good_urls, bad_searches


def thread_get_urls(driver, searchterm, dates, good_urls, bad_searches):
    self = threading.current_thread()
    self.result = get_urls(driver, searchterm, dates, good_urls, bad_searches)


def concurrent_get_urls(searchterms, dates, good_urls, bad_searches):
    threads = []
    drivers = [webdriver.Firefox() for i in xrange(len(searchterms))]
    for idx, searchterm in enumerate(searchterms):
        thread = threading.Thread(target=thread_get_urls,
                                  args=(drivers[idx], searchterm, dates, good_urls, bad_searches))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    results = []
    for thread in threads:
        results.append(thread.result)
    for result in results:
        good_urls = good_urls.union(result[0])
        bad_searches = bad_searches.union(result[1])
    for driver in drivers:
        driver.close()
    return good_urls, bad_searches


if __name__ == '__main__':
    ''' This script should be called in the following way:
    $ python fox_article_urls.py 'startdate' 'enddate'
    '''
    # Get all the keywords to search for
    searchterms = get_keywords_2016()

    start_date, end_date = argv[1], argv[2]
    print 'Scraping Fox News from {0} to {1}'.format(start_date, end_date)

    # Get dates to search over
    dates = get_week_tuples(start_date, end_date)

    # Initialize empty lists for urls to be appended to
    good_urls, bad_searches = set(), set()

    good_urls, bad_urls = concurrent_get_urls(
        searchterms[0:4], dates, good_urls, bad_searches)
    good_urls, bad_urls = concurrent_get_urls(
        searchterms[4:8], dates, good_urls, bad_searches)
    good_urls, bad_urls = concurrent_get_urls(
        searchterms[8:12], dates, good_urls, bad_searches)
    good_urls, bad_urls = concurrent_get_urls(
        searchterms[12:16], dates, good_urls, bad_searches)
    good_urls, bad_urls = concurrent_get_urls(
        searchterms[16:20], dates, good_urls, bad_searches)
    good_urls, bad_urls = concurrent_get_urls(
        searchterms[20:], dates, good_urls, bad_searches)

    print 'Fox Scraping Done...'
    print 'There were a total of {0} failed searches'.format(len(bad_searches))

    # If there were any bad searchs we should try and make some attempts to redo the searchs in a non-threaded way
    attempt = 0
    while attempt < 3 and len(bad_searches) > 0:
        # This will give us a tuple of (searchterm, date tuple) to research over
        searchterms_and_dates = list(bad_searches)
        # Reset our bad_searches to an empty set
        bad_searches = set()
        # Create a Firefox driver
        driver = webdriver.Firefox()
        for searchterm, date in searchterms_and_dates:
            good_urls, bad_searches = get_urls(driver, searchterm, [date], good_urls, bad_searches)
        driver.close()
        attempt += 1
        print 'Total of {0} failed searches after attempt {1}'.format(len(bad_searches), attempt)

    # Convert good_urls set to a list and write to a txt file
    file_path = '../url_files/{0}'.format(get_file_name('fox', start_date, end_date))
    with open(file_path, 'w') as f:
        f.write(json.dumps(list(good_urls)))
        f.close()

    # If there are any bad URLs, print how many there were and write them to a file for review
    print 'Number of Bad Searches = {0}'.format(len(bad_searches))
    if len(bad_searches):
        file_path = '../url_files/{0}'.format(get_file_name('fox', start_date, end_date, bad=True))
        with open(file_path, 'w') as f:
            f.write(json.dumps(list(bad_searches)))
            f.close()
