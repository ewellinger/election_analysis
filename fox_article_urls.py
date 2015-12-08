from selenium import webdriver
from bs4 import BeautifulSoup
import itertools
import json
import threading
from keywords import get_keywords_2016


def get_urls_from_search(driver, searchterm, date, attempt=0):
    searchterm = searchterm.replace(' ', '%20')
    url = 'http://www.foxnews.com/search-results/search?q={0}&ss=fn&section.path=fnc/politics&type=story&min_date={1}&max_date={1}&start=0'.format(searchterm, date)

    # Get the html from the site and create a BeautifulSoup object from it
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        # Get the number of search results.  If greater than 10 we'll need to loop through subsequent pages to get the additional urls
        num_found = int(soup.find('span', attrs = {'ng-bind': 'numFound'}).contents[0])

        if num_found <= 10:
            articles = soup.findAll('div', class_='search-article ng-scope')
            return True, [str(tag.find('a').get('href')) for tag in articles]
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
            return True, urls
    except:
        if attempt < 3:
            attempt += 1
            return get_urls_from_search(driver, searchterm, date, attempt)
        else:
            return False, url


def get_urls(driver, searchterm, dates, good_urls, bad_urls):
    for date in dates:
        response = get_urls_from_search(driver, searchterm, date)
        if response[0]:
            for url in response[1]:
                good_urls.add(url)
        else:
            bad_urls.add(response[1])
    return good_urls, bad_urls


def thread_get_urls(driver, searchterm, dates, good_urls, bad_urls):
    self = threading.current_thread()
    self.result = get_urls(driver, searchterm, dates, good_urls, bad_urls)


def concurrent_get_urls(searchterms, dates, good_urls, bad_urls):
    threads = []
    drivers = [webdriver.Firefox() for i in xrange(len(searchterms))]
    for idx, searchterm in enumerate(searchterms):
        thread = threading.Thread(target=thread_get_urls,
                                  args=(drivers[idx], searchterm, dates, good_urls, bad_urls))
        threads.append(thread)
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    results = []
    for thread in threads: results.append(thread.result)
    for result in results:
        good_urls = good_urls.union(result[0])
        bad_urls = bad_urls.union(result[1])
    return good_urls, bad_urls





if __name__=='__main__':
    # Get all the keywords to search for
    # searchterms = get_keywords_2016()
    searchterms = ['trump', 'carson', 'clinton']

    # Create the Firefox driver for selenium
    # driver = webdriver.Firefox()

    # Create list of invalid dates to exclude from search
    bad_dates = ['02-30', '02-31', '04-31', '06-31', '09-31', '11-31']
    bad_dates = ['2015-' + date for date in bad_dates]

    # Create list of all dates to search over
    # Note: This is only going up to December.  Will redo the scraping at a later date to get the days in December
    months, days = range(11, 12), range(1, 32)
    months = ['0' + str(month) if len(str(month)) == 1 else str(month) for month in months]
    days = ['0' + str(day) if len(str(day)) == 1 else str(day) for day in days]
    dates = itertools.product(months, days)
    dates = ['2015-' + date[0] + '-' + date[1] for date in dates]
    dates = [date for date in dates if date not in bad_dates]

    # Initialize empty lists for urls to be appended to
    good_urls, bad_urls = set(), set()

    # for searchterm in searchterms:
    #     good_urls, bad_search = get_urls(driver, searchterm, dates, good_urls, bad_urls)

    good_urls, bad_urls = concurrent_get_urls(searchterms, dates, good_urls, bad_urls)

    # Convert each set to a list and write to a txt file
    with open('./url_files/fox_article_urls_2016.txt', 'w') as f:
        f.write(json.dumps(list(good_urls)))
        f.close()
    with open('./url_files/bad_fox_article_urls_2016.txt', 'w') as f:
        f.write(json.dumps(list(bad_urls)))
        f.close()
