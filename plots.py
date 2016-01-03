import pandas as pd
import numpy as np
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from wordcloud import WordCloud
from cluster import topic_word_freq, nmf_articles


def plot_candidate_percentages(df, candidates):
    ''' This isn't that great of a function, might want to just delete it '''
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


def article_count_by_time(df, searchterm=None, topic=None, source=False, freq='W', normalize=False, show=True, marker='o', year=False, fig=None, label=None):
    outlets = [('nyt', 'NYT', '#4c72b0'), ('foxnews', 'FOX', '#c44e52'), ('npr', 'NPR', '#55a868'), ('guardian', 'GUA', '#8172b2'), ('wsj', 'WSJ', '#ccb974')]
    frequency = {'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly'}
    outlet_sizes = [len(df.loc[df['source'] == outlet]) for outlet in zip(*outlets)[0]]
    if topic:
        labels, label = topic
        df = df.loc[labels == label]
    if not searchterm and not source:
        ts = pd.Series([1], index=df['date_published']).resample(freq, how='sum').fillna(0)
        if not fig:
            fig = plt.figure(figsize=(12, 8))
        plt.subplots_adjust(left=0.08, bottom=0.12, right=0.95, top=0.92)
        ts.plot(marker=marker, label=label)
        plt.xlabel('Date Published ({})'.format(frequency[freq]))
        plt.ylabel('Article Count (freq={})'.format(freq))
    elif not searchterm and source:
        timeseries = [pd.Series([1], index=df.loc[df['source'] == outlet, 'date_published']).resample(freq, how='sum').fillna(0) for outlet in zip(*outlets)[0]]
        if normalize:
            timeseries = [ts / outlet_size for ts, outlet_size in zip(timeseries, outlet_sizes)]
        if not fig:
            fig = plt.figure(figsize=(12, 8))
        plt.subplots_adjust(left=0.08, bottom=0.12, right=0.95, top=0.92)
        for idx, ts in enumerate(timeseries):
            if len(ts):
                ts.plot(marker=marker, label=outlets[idx][1], c=outlets[idx][2])
        plt.xlabel('Date Published ({})'.format(frequency[freq]), fontsize=12)
        if normalize:
            plt.ylabel('Article Frequency (freq = {})'.format(freq), fontsize=12)
        else:
            plt.ylabel('Article Count (Freq = {})'.format(freq), fontsize=12)
        plt.legend(loc='best')
    elif searchterm and not source:
        ts = pd.Series(df['lemmatized_text'].str.contains(searchterm).astype('int').values, index=df['date_published']).resample(freq, how='sum').fillna(0)
        if not fig:
            fig = plt.figure(figsize=(12, 8))
        plt.subplots_adjust(left=0.08, bottom=0.12, right=0.95, top=0.92)
        ts.plot(marker=marker)
        plt.xlabel('Date Published ({})'.format(frequency[freq]), fontsize=12)
        plt.ylabel('Article Count (freq={})'.format(freq), fontsize=12)
        plt.title("Articles Containing '{}'".format(searchterm), fontsize=14)
    elif searchterm and source:
        timeseries = [pd.Series(df.loc[df['source'] == outlet, 'lemmatized_text'].str.contains(searchterm).astype('int').values, index=df.loc[df['source'] == outlet, 'date_published']).resample(freq, how='sum').fillna(0) for outlet in zip(*outlets)[0]]
        if normalize:
            timeseries = [ts / outlet_size for ts, outlet_size in zip(timeseries, outlet_sizes)]
        if not fig:
            fig = plt.figure(figsize=(12, 8))
        plt.subplots_adjust(left=0.08, bottom=0.12, right=0.95, top=0.92)
        for idx, ts in enumerate(timeseries):
            if len(ts):
                ts.plot(marker=marker, label=outlets[idx][1], c=outlets[idx][2])
        plt.xlabel('Date Published ({})'.format(frequency[freq]), fontsize=12)
        if normalize:
            plt.ylabel('Article Frequency (freq = {})'.format(freq), fontsize=12)
        else:
            plt.ylabel('Article Count (Freq = {})'.format(freq), fontsize=12)
        plt.legend(loc='best')
        plt.title("Articles Containing '{}'".format(searchterm), fontsize=14)
        plt.legend(loc='best')
    if year:
        plt.xlim((date(2014, 12, 20), date(2016, 1, 15)))
        if not normalize:
            axis = plt.axis()
            plt.ylim((0, axis[3] + 1))
    if show:
        plt.show()


def topic_time_and_cloud(df, topic, feature_names, nmf, title, mask_path=None, source=False, normalize=False, freq='W', year=True, max_words=300, show=True):
    fig = plt.figure(figsize=(14, 8.5))
    ax1 = fig.add_subplot(211)
    article_count_by_time(df, topic=topic, source=source, normalize=normalize, freq=freq, year=year, fig=fig, show=False)
    plt.suptitle(title, fontsize=20)

    outlets = [('nyt', 'NYT', '#4c72b0'), ('foxnews', 'FOX', '#c44e52'), ('npr', 'NPR', '#55a868'), ('guardian', 'GUA', '#8172b2'), ('wsj', 'WSJ', '#ccb974')]
    num_articles = np.sum(topic[0] == topic[1])
    percent_by_source = [float(len(df.loc[(topic[0] == topic[1]) & (df['source'] == outlet)])) / num_articles for outlet in zip(*outlets)[0]]
    normalized = [percent / np.sum(df['source'] == outlet) for percent, outlet in zip(percent_by_source, zip(*outlets)[0])]
    normalized = [percent / np.sum(normalized) for percent in normalized]

    byline = 'Number of Articles in Topic: {}\n'.format(num_articles)
    byline += '\t\t'.join(['{0}: {1:.1f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*outlets)[1], normalized)])

    plt.title(byline)
    plt.subplots_adjust(left=0.06, bottom=0.03, right=0.97, top=0.88, hspace=0.28)
    ax2 = fig.add_subplot(212)
    word_freq = topic_word_freq(nmf.components_, topic[1], feature_names)
    if mask_path:
        mask = np.array(Image.open(mask_path))
        wc = WordCloud(background_color='white', max_words=max_words, width=1900, height=500, mask=mask)
    else:
        wc = WordCloud(background_color='white', max_words=max_words, width=1900, height=500)
    wc.fit_words(word_freq)
    plt.imshow(wc)
    plt.axis('off')
    if show:
        plt.show()


def normalized_source_barchart(df, topic, outlets, ax=None):
    num_articles = np.sum(topic[0] == topic[1])
    percent_by_source = [float(len(df.loc[(topic[0] == topic[1]) & (df['source'] == outlet)])) / num_articles for outlet in zip(*outlets)[0]]
    normalized = [percent / np.sum(df['source'] == outlet) for percent, outlet in zip(percent_by_source, zip(*outlets)[0])]
    normalized = [percent / np.sum(normalized) for percent in normalized]

    if not ax:
        fig, ax = plt.subplots(1, figsize=(2,5))
    for idx, percent in enumerate(normalized):
        plt.bar(0, percent, width=0.2, label=outlets[idx][1], color=outlets[idx][2], bottom=np.sum(normalized[:idx]))
    plt.legend(loc='best')
    plt.axis('off')
    plt.show()



if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    # Plot % of articles mentioning candidate accross all news sources
    # plot_candidate_percentages(df, ['Clinton', 'Trump', 'Bush'])

    tfid, nmf, X, W, labels, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=80, n_features=15000, random_state=1, max_df=0.9, min_df=2)

    outlets = [('nyt', 'NYT', '#4c72b0'), ('foxnews', 'FOX', '#c44e52'), ('npr', 'NPR', '#55a868'), ('guardian', 'GUA', '#8172b2'), ('wsj', 'WSJ', '#ccb974')]
    for idx, words in enumerate(topic_words):
        num_articles = len(labels[labels == idx])
        articles_by_source = [float(len(df.loc[(labels == idx) & (df['source'] == outlet)])) / num_articles for outlet in zip(*outlets)[0]]
        print 'Label {}'.format(idx)
        print words
        print 'Number of articles in topic: {}'.format(num_articles)
        print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*outlets)[1], articles_by_source)])
        normalized = [percent / len(df.loc[df['source'] == outlet]) for percent, outlet in zip(articles_by_source, zip(*outlets)[0])]
        normalized = [percent / np.sum(normalized) for percent in normalized]
        print 'Normalized Percentages'
        print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*outlets)[1], normalized)])
        print '\n'
