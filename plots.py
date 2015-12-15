import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_canidate_percentages(df, canidates):
    outlets = np.array(['nyt', 'npr', 'foxnews', 'guardian', 'wsj'])
    ind = np.arange(5)
    c = ['#4e73ad', '#c12e1d', '#ebc844', '#a2b86b']
    width = 0.25
    for i, canidate in enumerate(canidates):
        percentages = np.array([df.loc[df['source'] == outlet, 'article_text'].str.contains(canidate.lower()).sum() / float(len(df[df['source'] == outlet])) for outlet in outlets])
        # idx = np.argsort(percentages)[::-1]
        # outlets, percentages = outlets[idx], percentages[idx]
        plt.bar(ind + i*width, percentages, width, color=c[i], label=canidate)
    plt.title('Coverage By News Outlet')
    plt.xticks(ind + (width/2.) * len(canidates), outlets)
    plt.ylabel('Percentage of Articles Mentioning Canidate')
    plt.xlabel('News Outlet')
    plt.legend(loc='best')
    plt.show()


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    plot_canidate_percentages(df, ['Clinton', 'Trump', 'Bush'])
