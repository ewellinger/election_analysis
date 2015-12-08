import itertools


# Defines all the keywords associated with the 2016 election cycle
def get_keywords_2016():
    keywords = ['jeb bush', 'carson', 'christie', 'cruz', 'fiorina', 'jim gilmore', 'lindsey graham', 'huckabee', 'kasich', 'george pataki', 'rand paul', 'rubio', 'santorum', 'trump', 'rick perry', 'scott walker', 'jindal', 'clinton', "o'malley", 'omalley', 'sanders', 'jim webb', 'chafee', 'lessig']
    return keywords


def get_dates(start_mon=1, end_mon=13, start_day=1, end_day=31):
    bad_dates = ['02-30', '02-31', '04-31', '06-31', '09-31', '11-31']
    bad_dates = ['2015-' + date for date in bad_dates]

    # Create list of all dates to search over
    months, days = range(start_mon, end_mon), range(start_day, end_day)
    months = ['0' + str(month) if len(str(month)) == 1 else str(month) for month in months]
    days = ['0' + str(day) if len(str(day)) == 1 else str(day) for day in days]
    dates = itertools.product(months, days)
    dates = ['2015-' + date[0] + '-' + date[1] for date in dates]
    dates = [date for date in dates if date not in bad_dates]
    return dates
