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


def get_dates(start_mon=1, end_mon=12, start_day=1, end_day=None):
    if not end_day:
        end_day = days_in_month[end_mon]
    start_date = '2015-{0}-{1}'.format(get_num_str(start_mon), get_num_str(start_day))
    end_date = '2015-{0}-{1}'.format(get_num_str(end_mon), get_num_str(end_day))

    date_range = pd.date_range(start_date, end_date, freq='D')
    date_range = [date.strftime('%Y-%m-%d') for date in date_range]
    return date_range


def get_week_tuples(start_mon=1, end_mon=12):
    date = ('2015-{}-01'.format(get_num_str(start_mon)), '2015-{0}-{1}'.format(get_num_str(end_mon), get_num_str(days_in_month[end_mon])))
    date_range = pd.date_range(date[0], date[1], freq='W')
    date_range = [date.strftime('%Y-%m-%d') for date in date_range]
    result = [('2015-'+get_num_str(start_mon)+'-01', date_range[0])]
    for i in zip(date_range[:], date_range[1:]):
        result.append(i)
    result.append((date_range[-1], '2015-'+get_num_str(end_mon)+ '-' + get_num_str(days_in_month[end_mon])))
    return result

days_in_month = {1: 31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}


def get_num_str(num):
    if len(str(num)) == 1:
        return '0' + str(num)
    else:
        return str(num)


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
    return stopwords.words('english') + ['guardian', 'new york times', 'nyt', 'wall street journal', 'wsj', 'mr', 'mrs', 'ms', 'gov', 'sen', 'rep', 'said', 'fox', 'would', 'campaign', 'candidate', 'washingtonexaminercom', 'npr']


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
    'franci': 'francis'
    }
    return correct_lemma


def topic_labels():
    '''
    OUTPUT: dict - A dictionary relating the topic index to a text label describing what the topic is about.
    *** This is only correct when performing the nmf_articles function with the following parameters... nmf_articles(df, n_topics=100, n_features=10000, random_state=1, max_df=0.8, min_df=5).  Without setting the random_state to 1, the order of the subsequent topics will NOT be the same ***
    '''
    topic_label = {
    0: 'junk',
    1: 'Classified Information', # Related to the Clinton Email Scandal but focuses on the investigation
    2: 'Donald Trump',
    3: 'Political Polling',
    4: "Clinton's Email Server",
    5: 'Taxes / Economy',
    6: 'Jeb Bush',
    7: 'Marco Rubio',
    8: 'Joe Biden',
    9: 'Political Polling', # Should be combined with topic 3
    10: 'Super PAC (Political Finance)',
    11: 'Scott Walker',
    12: 'Syrian Refugees',
    13: 'Hillary Clinton',
    14: 'Planned Parenthood',
    15: 'Vaccination / Measles Outbreak',
    16: 'Ted Cruz',
    17: 'Same-Sex Marriage',
    18: 'NSA / Bulk Collection',
    19: 'Ben Carson',
    20: 'Chris Christie',
    21: 'Gun Control',
    22: 'Political Debate',
    23: 'Carly Fiorina',
    24: 'Rand Paul',
    25: 'Iowa Caucuses',
    26: 'Minimum Wage',
    27: 'Police Brutality / Black Lives Matter / Baltimore',
    28: 'Affordable Care Act',
    29: 'Rick Perry',
    30: 'Iran Nuclear Deal',
    31: 'De Blasio', # This is very New York focused
    32: "Martin O'Malley",
    33: 'Climate Change / Keystone Pipeline',
    34: 'Muslim / Ban', # Also mentions Bernadino a bit
    35: 'Lincoln Chafee',
    36: 'junk', # Spanish topic
    37: 'Mitt Romney',
    38: 'Political Ads',
    39: 'Barack Obama',
    40: 'Immigration',
    41: "Woman's Rights", # You should look up why the term 'beij' is showing up in this topic
    42: 'John Kasich',
    43: 'DNC Data Breach',
    44: 'Mike Huckabee',
    45: 'Speaker of the House',
    46: 'Cuban Relations',
    47: 'Drug Pricing / Martin Shkreli',
    48: 'Budget',
    49: 'Bobby Jindal',
    50: 'Lindsey Graham',
    51: 'Israeli / Palestinian',
    52: 'Trans-Pacific Partnership',
    53: 'Libya Memo (Benghazi)', # This is closely related with the more general Benghazi topic
    54: 'Koch Brothers',
    55: 'Lawrence Lessig',
    56: 'Union / Labor',
    57: 'Rudy Giuliani',
    58: 'Jim Webb',
    59: 'David Wildstein (Bridge Scandal)', # This should probably get combined with the more general Chris Christie Bridge Scandal topic
    60: 'Charleston / Confederate Flag',
    61: 'Higher Education',
    62: 'Gateway Project (Amtrak Rail Corridor)',
    63: 'Supreme Court',
    64: 'China',
    65: 'Congress',
    66: 'junk',
    67: 'Clinton Foundation',
    68: 'Wall Street',
    69: 'Criminal Justice System',
    70: 'junk',
    71: 'junk', # Fox news Power play topic
    72: 'Political Fundraising',
    73: 'ISIS (Iraq / Syria)',
    74: 'State Department (Clinton Aides)', # Rename this one
    75: 'Talk Shows',
    76: "Louisiana Governor's Race",
    77: 'Elizabeth Warren',
    78: 'junk', # WSJ column
    79: 'Puerto Rico Bankruptcy',
    80: 'junk', # Howard Kurtz, Fox news column
    81: 'Political Parties',
    82: 'Andrew Cuomo', # You should look into what articles are in here
    83: 'Marijuana',
    84: 'Publishing', # Inlucdes 'schweizer' for some reason
    85: 'Bernie Sanders',
    86: 'Trump Mexican Comment',
    87: 'junk', # Fox News Column
    88: 'Terrorist Attack (Paris / San Bernadino)',
    89: 'Education System',
    90: 'Minority Voting',
    91: 'Religious Liberty',
    92: 'John McCain', # Heavily connected to Trump's comment about McCain
    93: 'junk', # NYT, random words
    94: 'New Hampshire Primary',
    95: 'Kim Davis',
    96: 'Theater (junk)',
    97: 'Pope Francis',
    98: 'SuperPAC / Political Donations',
    99: 'Benghazi Committee'
    }
    return topic_label

# Both the first two fox article url files had 3157 urls
