from bs4 import BeautifulSoup
from requests import get
import os
# Import WSJ Access Credentials from zsh profile
user_name = os.environ['WSJ_USER_ACCOUNT']
password = os.environ['WSJ_PASSWORD']


if __name__=='__main__':
    date = '2015-11-12'
    url = 'http://www.wsj.com/public/page/archive-{0}.html'.format(date)

    html = get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
