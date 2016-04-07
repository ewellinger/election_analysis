import pandas as pd
from unidecode import unidecode
from nltk.corpus import stopwords


# Defines all the keywords associated with the 2016 election cycle
def get_keywords_2016():
    keywords = ['jeb bush', 'carson', 'christie', 'cruz', 'fiorina', 'jim gilmore', 'lindsey graham', 'huckabee', 'kasich', 'george pataki', 'rand paul', 'rubio', 'santorum', 'trump', 'rick perry', 'scott walker', 'jindal', 'clinton', "o'malley", 'omalley', 'sanders', 'jim webb', 'chafee', 'lessig', 'biden']
    return keywords


def get_canidate_names_2016():
    keywords = ['jeb bush',
                'ben carson',
                'chris christie',
                'ted cruz',
                'carly fiorina',
                'jim gilmore',
                'lindsey graham',
                'mike huckabee',
                'john kasich',
                'george pataki',
                'rand paul',
                'marco rubio',
                'rick santorum',
                'donald trump',
                'rick perry',
                'scott walker',
                'bobby jindal',
                'hillary clinton', 'hillary rodham clinton',
                "martin o'malley",
                'martin omalley',
                'bernie sanders',
                'jim webb',
                'lincoln chafee',
                'lawrence lessig',
                'joe biden', 'joseph biden']
    return '|'.join(keywords)


def get_dates(start_date, end_date):
    ''' Returns a list of dates in 'YYYY-MM-DD' format
    INPUT:
        start_date - string in 'YYYY-MM-DD' or 'YYYY-M-DD' format
        end_date - string in 'YYYY-MM-DD' or 'YYYY-M-DD' format
    OUTPUT:
        list of date strings at a daily frequency
    '''
    date_range = pd.date_range(start_date, end_date, freq='D')
    date_range = [date.strftime('%Y-%m-%d') for date in date_range]
    return date_range


def get_week_tuples(start_date, end_date):
    ''' Returns a list of weekly tuples
    INPUT:
        start_date - string in 'YYYY-MM-DD' or 'YYYY-M-DD' format
        end_date - string in 'YYYY-MM-DD' or 'YYYY-M-DD' format
    OUPUT:
        list of string tuples representing dates at a weekly frequency (except for the first and last which will capture any days that started or ended mid-week) in ('YYYY-MM-DD', 'YYYY-MM-DD') format
    '''
    # Ensure that the date strings are in YYYY-MM-DD format
    start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')

    # Create list of dates at a weekly frequency
    date_range = pd.date_range(start_date, end_date, freq='W')
    date_range = [date.strftime('%Y-%m-%d') for date in date_range]

    # Create a list of weekly tuples that includes both the starting and ending dates
    result = []
    if start_date != date_range[0]:
        result.append((start_date, date_range[0]))
    result.extend(zip(date_range[:], date_range[1:]))
    if end_date != date_range[-1]:
        result.append((date_range[-1], end_date))
    return result


# Load list from file
def load_urls(filename):
    urls = ''
    with open(filename, 'r') as f:
        for line in f:
            urls += line
    urls = urls[1: -1].split(',')
    urls = [url.replace('"', '') for url in urls]
    urls = [url.replace(' ', '') for url in urls]
    return urls


def parse_str(x):
    if type(x) == unicode:
        return unidecode(x)
    else:
        return str(x)


def stop_words():
    return stopwords.words('english') + ['guardian', 'new york times', 'nyt', 'wall street journal', 'wsj', 'mr', 'mrs', 'ms', 'gov', 'sen', 'rep', 'said', 'fox', 'would', 'campaign', 'candidate', 'washingtonexaminercom', 'npr', 'httpwwwwashingtonexaminercomarticle']


def fix_lemmatized_words():
    '''
    OUTPUT: dict - A dictionary mapping the lemmatized word to what the word should actually be.
    The lemmatizer generally works well but shortens some words incorrectly (e.g. 'texas' -> 'texa', 'paris' -> 'pari', 'fetus' -> 'fetu').  This dictionary will correct some of the more blatent errors after lemmatizing
    '''
    correct_lemma = {
    'pari': 'paris',
    'infectiou': 'infectious',
    'dangerou': 'dangerous',
    'texa': 'texas',
    'religiou': 'religious',
    'chri': 'chris',
    'congres': 'congress',
    'hatre': 'hatred',
    'isi': 'isis',
    'massachusett': 'massachusetts',
    'arkansa': 'arkansas',
    'ridiculou': 'ridiculous',
    'abba': 'abbas',
    'campu': 'campus',
    'fundrais': 'fundraise',
    'crisi': 'crisis',
    'cannabi': 'cannabis',
    'sander': 'sanders',
    'davi': 'davis',
    'franci': 'francis',
    'orlean': 'orleans'
    }
    return correct_lemma


def get_topic_labels():
    '''
    OUTPUT: dict - A dictionary relating the topic index to a text label describing what the topic is about.
    *** This is only correct when performing the nmf_articles function with the following parameters... nmf_articles(df, n_topics=100, n_features=10000, random_state=1, max_df=0.8, min_df=5).  Without setting the random_state to 1, the order of the subsequent topics will NOT be the same ***
    '''
    topic_label = {
    0: 'junk',
    1: "Clinton's Email Server",
    2: 'Donald Trump',
    3: 'Political Polling',
    4: 'Jeb Bush',
    5: 'Bernie Sanders',
    6: 'Taxes / Economy',
    7: 'Joe Biden',
    8: 'Chris Christie',
    9: 'Ben Carson',
    10: 'Terrorist Attack (Paris / San Bernadino)',
    11: 'Political Donations',
    12: 'Gun Control',
    13: 'Scott Walker',
    14: 'Ted Cruz',
    15: 'Super PAC',
    16: 'junk',
    17: 'Rand Paul',
    18: 'Same-Sex Marriage',
    19: 'Political Debates',
    20: 'Planned Parenthood',
    21: 'Iran Nuclear Deal',
    22: 'Marco Rubio',
    23: 'Mitt Romney',
    24: 'Carly Fiorina',
    25: 'Law Enforcement',
    26: 'President Obama',
    27: 'Charleston / Confederate Flag',
    28: 'Climate Change',
    29: 'Higher Education',
    30: 'Syrian Refugees',
    31: "Martin O'Malley",
    32: 'NSA / Bulk Collection',
    33: 'Rick Perry',
    34: 'Minimum Wage',
    35: 'Trans-Pacific Partnership',
    36: 'Lindsey Graham',
    37: 'Union / Labor',
    38: 'Cuban Relations',
    39: 'Affordable Care Act',
    40: 'Marijuana',
    41: 'junk', # Spanish topic
    42: 'Political Ads',
    43: 'Mike Huckabee',
    44: 'Gateway Project (Amtrak Rail Corridor)',
    45: 'Israeli / Palestinian',
    46: 'Clinton Foundation',
    47: 'Lincoln Chafee',
    48: 'Bobby Jindal',
    49: "Louisiana Governor's Race",
    50: 'John Kasich',
    51: 'Howard Kurtz / Journalism',
    52: 'Black Lives Matter',
    53: 'Kim Davis',
    54: 'junk', # Fox news column
    55: 'Speaker of the House',
    56: 'Wall Street',
    57: 'Exxon Settlement',
    58: 'Pope Francis',
    59: 'Elizabeth Warren',
    60: 'New Hampshire Primary',
    61: 'Theater (junk)',
    62: 'junk', # WSJ column
    63: 'ISIS (Iraq / Syria)',
    64: 'Drug Pricing / Martin Shkreli',
    65: 'Immigration',
    66: 'junk', # Various general words
    67: 'George Pataki',
    68: 'Jim Webb',
    69: 'junk', # General journalism words
    70: 'Libya Memo (Benghazi)', # This is closely related with the more general Benghazi topic
    71: 'State Department (Benghazi)', # Also closely related to the Benghazi topic
    72: 'Rick Santorum',
    73: 'Attorney General',
    74: 'Iraq War',
    75: 'Trump Mexican Comment',
    76: 'Keystone Pipeline',
    77: 'Political Polling',
    78: 'Talk Shows',
    79: 'Russian Relations',
    80: 'Iowa Cacuses',
    81: 'De Blasio', # This is very New York focused
    82: 'Hillary Clinton',
    83: 'Benghazi Committee',
    84: "Trump's Muslim Ban",
    85: 'Supreme Court',
    86: 'Congress',
    87: 'Budget',
    88: 'Political Parties', # This seems to be more focused on the Republican Party
    89: 'junk' # Just words about when and what time an article was published
    }
    return topic_label
