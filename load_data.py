import pandas as pd


# Defines all the keywords associated with the 2016 election cycle
def get_keywords_2016():
    keywords = ['jeb bush', 'carson', 'christie', 'cruz', 'fiorina', 'jim gilmore', 'lindsey graham', 'huckabee', 'kasich', 'george pataki', 'rand paul', 'rubio', 'santorum', 'trump', 'rick perry', 'scott walker', 'jindal', 'clinton', "o'malley", 'omalley', 'sanders', 'jim webb', 'chafee', 'lessig', 'biden']
    return keywords


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
