import pandas as pd
import numpy as np


def create_shootings_df():
    '''
    Return DataFrame with data on all Mass Shootings occuring in 2015.
    Data provided by Gun Violence Archive (http://www.gunviolencearchive.org/reports/mass-shootings/2015)
    '''
    df = pd.read_csv('mass_shootings_2015.csv', parse_dates=[0])
    col_names = {'# Killed': 'killed',
                 '# Injured': 'injured',
                 'Incident Date': 'date',
                 'State': 'state',
                 'City Or County': 'city_county',
                 'Address': 'address'
                 }
    df = df.rename(columns=col_names).drop('Operations', axis=1)
    df['casualties'] = df['killed'] + df['injured']
    df.sort_values('casualties', ascending=False, inplace=True)
    df = df.reset_index(drop=True)
    return df


if __name__=='__main__':
    msdf = create_shootings_df()
