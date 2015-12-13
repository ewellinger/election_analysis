from bs4 import BeautifulSoup
from selenium import webdriver
import os
import json
# Import WSJ Access Credentials from zsh profile
user_name = os.environ['WSJ_USER_ACCOUNT']
password = os.environ['WSJ_PASSWORD']


def log_in_wsj():
    url = 'https://id.wsj.com/access/pages/wsj/us/signin.html?url=http%3A%2F%2Fwww.wsj.com&mg=id-wsj'


if __name__=='__main__':
    urls = load_urls('./url_files/wsj_article_urls_2016.txt')
    
