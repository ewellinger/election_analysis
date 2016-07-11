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


def get_week_tuples(start_date, end_date, strf='%Y-%m-%d'):
    ''' Returns a list of weekly tuples
    INPUT:
        start_date - string in 'YYYY-MM-DD' or 'YYYY-M-DD' format
        end_date - string in 'YYYY-MM-DD' or 'YYYY-M-DD' format
        strf - string denoting the date format
    OUPUT:
        list of string tuples representing dates at a weekly frequency (except for the first and last which will capture any days that started or ended mid-week) in ('YYYY-MM-DD', 'YYYY-MM-DD') format
    '''
    # Ensure that the date strings are in YYYY-MM-DD format
    start_date = pd.to_datetime(start_date).strftime(strf)
    end_date = pd.to_datetime(end_date).strftime(strf)

    # Create list of dates at a weekly frequency
    date_range = pd.date_range(start_date, end_date, freq='W')
    date_range = [date.strftime(strf) for date in date_range]

    if len(date_range) == 0:
        return [(start_date, end_date)]

    # Create a list of weekly tuples that includes both the starting and ending dates
    result = []
    if start_date != date_range[0]:
        result.append((start_date, date_range[0]))
    result.extend(zip(date_range[:], date_range[1:]))
    if end_date != date_range[-1]:
        result.append((date_range[-1], end_date))
    return result


def get_file_name(source, start_date, end_date, bad=False):
    ''' Returns a filename for a given search (e.g. fox_20160101_20160201.txt) '''
    # Ensure that the date strings are in YYYYMMDD format
    start_date = pd.to_datetime(start_date).strftime('%Y%m%d')
    end_date = pd.to_datetime(end_date).strftime('%Y%m%d')
    if bad:
        return '{0}_{1}_{2}_bad.txt'.format(source, start_date, end_date)
    else:
        return '{0}_{1}_{2}.txt'.format(source, start_date, end_date)


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
    if isinstance(x, unicode):
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
    'orlean': 'orleans',
    'vega': 'vegas',
    'kansa': 'kansas'
    }
    return correct_lemma


def get_topic_labels():
    '''
    OUTPUT: dict - A dictionary relating the topic index to a text label describing what the topic is about.
    *** This is only correct when creating the NMFClustering object with the default parameters and the DataFrame object containing news articles ranging from 2015-01-01 to 2015-05-15.  If any of the attributes are changed, the order of the subsequent topics could be different ***
    '''
    topic_label = {
        1: 'Donald Trump',
        2: 'Bernie Sanders',
        3: 'Clinton Email Server',
        4: 'Classified Information/Email Server',
        5: 'State Delegates',
        6: 'Political Polling',
        7: 'Political Polling',
        8: 'Chris Christie',
        9: 'Marco Rubio',
        10: 'Political Debates',
        11: 'Joe Biden',
        12: 'Scott Walker',
        13: 'Political Fundraising',
        14: 'Candidacy Announcement',
        15: 'Ben Carson',
        16: 'Ted Cruz',
        17: 'Gun Control',
        18: 'Union/Labor',
        20: 'De Blasio',
        21: 'NRA',
        22: 'Iran Nuclear Agreement',
        23: 'John Kasich',
        24: 'Planned Parenthood',
        25: 'Trans-Pacific Partnership',
        26: 'Rand Paul',
        27: 'Black Lives Matter',
        28: "Fiorina/HP",
        29: 'Immigration',
        30: 'Benghazi Committee',
        31: 'Carly Fiorina',
        33: 'President Obama',
        34: "Martin O'Malley",
        35: 'Energy Industry',
        37: 'Lindsey Graham',
        38: 'Climate Change',
        39: 'Hillary Clinton',
        40: "Women's Equality",
        42: 'Rick Perry',
        43: 'Presumptive Nominee',
        44: 'Syrian Refugees',
        45: 'Muslim Ban',
        46: 'NSA Surveillance',
        47: 'Minimum Wage',
        48: 'Mitt Romney',
        49: 'Paul Ryan',
        51: 'Clinton Foundation',
        52: 'Pope Francis',
        54: 'Israel/Netanyahu',
        55: 'Affordable Care Act',
        56: 'Cuban Relations',
        57: 'Higher Education',
        58: 'Political Polling',
        59: 'Port Authority',
        61: 'Political Endorsement',
        64: 'Same-Sex Marriage',
        65: 'Bobby Jindal',
        67: 'Super PACs',
        68: 'Israel',
        69: 'John Boehner',
        70: 'Wall Street',
        71: 'Mike Huckabee',
        72: 'Financial Industry',
        73: 'Law Enforcement',
        74: 'Political Rally',
        77: 'Sarah Palin',
        78: 'Latino Community',
        80: 'Koch Brothers',
        81: 'Lincoln Chafee',
        82: 'Fiscal Budget',
        83: 'Flint Water Crisis',
        84: 'Amtrak Tunnel Project',
        85: 'Religious Liberty',
        87: 'John McCain',
        90: 'Civil/LGBT Rights',
        91: 'Drug Addiction',
        93: 'Confederate Flag',
        94: 'Iowa Caucus',
        96: 'Tax Plan',
        97: "Women's Health/Abortion",
        98: 'Sidney Blumenthal/Libya Email',
        99: 'South Carolina Primary',
        100: 'Pharmaceutical Pricing',
        101: 'White House Press Briefings',
        102: 'Keystone Oil Pipeline',
        103: 'Chinese Economy',
        104: 'DNC Data Breach',
        105: 'Iraq War',
        106: "The Reagans",
        108: 'Michael Bloomberg',
        109: 'Hispanic Community',
        110: 'Nikki Haley',
        111: 'Economy',
        112: 'Marijuana',
        113: 'Corey Lewandowski',
        118: 'Rick Santorum',
        120: 'Elizabeth Warren',
        121: 'Jim Webb',
        122: 'The Federal Reserve',
        123: 'Loretta Lynch/Attorney General',
        124: 'Law Enforcement',
        125: 'Supreme Court',
        126: 'Kim Davis (KY County Clerk)',
        128: 'Russia/Vladimir Putin',
        129: 'New Hampshire Primary',
        131: 'Jeb Bush',
        132: 'U.S. Senate',
        134: 'Merrick Garland',
        135: 'Pension Fund',
        136: 'Exxon Settlement',
        138: 'Evangelical/Christian',
        139: 'Obamacare (Repeal Effort)',
        140: 'Coal',
        141: 'D. Wasserman Schultz',
        143: 'George Pataki',
        144: 'Stephen Colbert',
        145: 'Education',
        146: 'Stock Market',
        148: 'State Department',
        149: 'Paid Family Leave',
        150: 'Wisconsin/Labor',
        151: 'Bush Family',
        152: 'McCarthy Benghazi Comment',
        153: 'ISIS/Syria',
        154: 'Social Media',
        155: "Louisiana Governor's Race",
        156: 'Veteran Affairs',
        157: 'Puerto Rico Debt Crisis',
        161: 'Paris Terrorist Attack',
        162: 'Jobs/Manufacturing',
        163: 'Democratic Superdelegates',
        164: 'Prison System',
        165: 'YouTube',
        167: 'Vaccination',
        169: 'Protest Rally',
        171: 'FBI Investigation',
        175: 'Cleveland Convention',
        176: 'Jim Gilmore',
        178: 'San Bernardino Attak/Immigration Enforcement',
        181: 'Immigration Reform',
        183: 'Policy/Relations',
        184: 'Intelligence', # Very Fox oriented
        186: 'David Duke', # **
        190: 'Speech',
        191: 'Income Inequality',
        192: 'Lawrence Lessig',
        194: 'Military/Defense',
        196: 'Political Contributions',
        197: 'Paul Manafort (Trump Advisor)',
        198: 'Clinton Email Server',
        199: 'Common Core',
        201: 'Litigation',
        202: 'Saudi Arabia',
        203: 'North Korea',
        204: 'Caucus',
        205: 'Contest Results',
        206: 'NJ Bridge Scandal',
        208: 'Political Aide',
        209: 'Talk Shows',
        212: 'Antonin Scalia', # **
        214: 'Op-Ed',
        216: 'Congressional Legislation',
        221: 'Social Security',
        222: "Clinton's Benghazi Testimony",
        225: 'Guantanamo Bay Detainees',
        231: 'Corporations',
        233: 'Death Penalty',
        234: 'Ethanol',
        235: 'Citizenship',
        236: 'Megyn Kelly',
        237: 'Democratic Primary',
        238: 'U.S./Mexico Border Wall', # **
        239: 'Sen. Robert Menendez',
        240: 'Islamic State/ISIS/ISIL',
        241: 'Charleston Church Shooting',
        246: 'Miss America Pageant'
    }
    return topic_label


def get_candidate_info():
    ''' Return dict of information for each political candidate
    Returns topic_num associated with candidate, announcement date, and withdrawl date
    '''
    candidate_info = {
        'bush': [131, '2015-06-15', '2016-02-20'],
        'carson': [15, '2015-05-04', '2016-03-02'],
        'christie': [8, '2015-06-30', '2016-02-10'],
        'cruz': [16, '2015-03-23', '2016-05-03'],
        'fiorina': [31, '2015-05-04', '2016-02-10'],
        'gilmore': [176, '2015-07-30', '2016-02-12'],
        'graham': [37, '2015-06-01', '2015-12-21'],
        'huckabee': [71, '2015-05-05', '2016-02-01'],
        'kasich': [23, '2015-07-21', '2016-05-04'],
        'pataki': [143, '2015-05-28', '2015-12-29'],
        'paul': [26, '2015-04-17', '2016-02-03'],
        'rubio': [9, '2015-04-13', '2016-03-15'],
        'santorum': [118, '2015-05-27', '2016-02-03'],
        'trump': [1, '2015-06-16', None],
        'perry': [42, '2015-06-04', '2015-09-11'],
        'walker': [12, '2015-07-13', '2015-09-21'],
        'jindal': [65, '2015-06-24', '2015-11-17'],
        'clinton': [39, '2015-04-12', None],
        'omalley': [34, '2015-05-30', '2016-02-01'],
        'sanders': [2, '2015-04-30', None],
        'webb': [121, '2015-07-02', '2015-10-20'],
        'chafee': [81, '2015-06-03', '2015-10-23'],
        'lessig': [192, '2015-09-06', '2015-11-02'],
        'biden': [11, None, '2015-10-21']
    }
    return candidate_info


# Might be a cool plot to show both of the law enforcement plots and point to how they are about similar subjects but coming from different angles (i.e. Police brutality vs. the law in a more general sense)
# Maybe disregard any topic that has less than 30 articles attributed to it?
# Point out the number of topics associated with the Benghazi event (152, 30, 98, 222)
# Social Issues predominantly reported on by the guardian (169, 178, 233, 241)
# Topic 188, 195, 228, 238 are good examples of topics that don't really mean anything
# Maybe look into all the different topics revolving around the Clinton Email controversy (3, 4, 98, 198)
