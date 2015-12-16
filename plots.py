import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_candidate_percentages(df, candidates):
    outlets = np.array(['nyt', 'npr', 'foxnews', 'guardian', 'wsj'])
    ind = np.arange(5)
    c = ['#4e73ad', '#c12e1d', '#ebc844', '#a2b86b']
    width = 0.25
    for i, candidate in enumerate(candidates):
        percentages = np.array([df.loc[df['source'] == outlet, 'article_text'].str.contains(candidate.lower()).sum() / float(len(df[df['source'] == outlet])) for outlet in outlets])
        # idx = np.argsort(percentages)[::-1]
        # outlets, percentages = outlets[idx], percentages[idx]
        plt.bar(ind + i*width, percentages, width, color=c[i], label=candidate)
    plt.title('Coverage By News Outlet')
    plt.xticks(ind + (width/2.) * len(candidates), outlets)
    plt.ylabel('Percentage of Articles Mentioning Candidate')
    plt.xlabel('News Outlet')
    plt.legend(loc='best')
    plt.show()


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    # Plot % of articles mentioning candidate accross all news sources
    plot_candidate_percentages(df, ['Clinton', 'Trump', 'Bush'])
