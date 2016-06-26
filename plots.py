import pandas as pd
import numpy as np
from datetime import date
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud
from cluster import topic_word_freq, nmf_articles, print_topic_summary
from load_data import get_topic_labels
from shootings import create_shootings_df
plt.style.use('ggplot')


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
        labels, label_num = topic
        df = df.loc[labels[:, label_num]]
    if not fig:
        fig = plt.figure(figsize=(14, 8))
        fig.text(0.05, 0.03, 'Author: Erich Wellinger', fontsize=10, alpha=0.7)
        fig.text(0.33, 0.75, 'github.com/ewellinger/election_analysis', fontsize=20, color='gray', alpha=0.5)
    if not searchterm and not source:
        ts = pd.Series([1], index=df['date_published']).resample(freq, how='sum').fillna(0)
        plt.subplots_adjust(left=0.05, bottom=0.1, right=0.97, top=0.92)
        ts.plot(marker=marker, label=label)
        plt.xlabel('Date Published ({})'.format(frequency[freq]))
        plt.ylabel('Article Count (freq={})'.format(freq))
    elif not searchterm and source:
        timeseries = [pd.Series([1], index=df.loc[df['source'] == outlet, 'date_published']).resample(freq, how='sum').fillna(0) for outlet in zip(*outlets)[0]]
        if normalize:
            timeseries = [ts / outlet_size for ts, outlet_size in zip(timeseries, outlet_sizes)]
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
        plt.title(label)
    elif searchterm and not source:
        ts = pd.Series(df['lemmatized_text'].str.contains(searchterm).astype('int').values, index=df['date_published']).resample(freq, how='sum').fillna(0)
        plt.subplots_adjust(left=0.08, bottom=0.12, right=0.95, top=0.92)
        ts.plot(marker=marker)
        plt.xlabel('Date Published ({})'.format(frequency[freq]), fontsize=12)
        plt.ylabel('Article Count (freq={})'.format(freq), fontsize=12)
        plt.title("Articles Containing '{}'".format(searchterm), fontsize=14)
    elif searchterm and source:
        timeseries = [pd.Series(df.loc[df['source'] == outlet, 'lemmatized_text'].str.contains(searchterm).astype('int').values, index=df.loc[df['source'] == outlet, 'date_published']).resample(freq, how='sum').fillna(0) for outlet in zip(*outlets)[0]]
        if normalize:
            timeseries = [ts / outlet_size for ts, outlet_size in zip(timeseries, outlet_sizes)]
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


def topic_time_and_cloud(df, topic, feature_names, nmf, title, source=False, normalize=False, freq='W', year=True, max_words=300, positivity=True, show=True):
    fig = plt.figure(figsize=(14, 8.5))
    ax1 = fig.add_axes([0.05, 0.5, 0.93, 0.41])
    article_count_by_time(df, topic=topic, source=source, normalize=normalize, freq=freq, year=year, fig=fig, label=topic_labels[topic[1]], show=False)
    ax1.xaxis.labelpad = -4
    plt.suptitle(title, fontsize=20)

    fig.text(0.05, 0.44, 'Author: Erich Wellinger', fontsize=10, alpha=0.7)
    fig.text(0.33, 0.8, 'github.com/ewellinger/election_analysis', fontsize=20, color='gray', alpha=0.5)

    outlets = [('nyt', 'NYT', '#4c72b0'), ('foxnews', 'FOX', '#c44e52'), ('npr', 'NPR', '#55a868'), ('guardian', 'GUA', '#8172b2'), ('wsj', 'WSJ', '#ccb974')]

    # Create a boolean mask for whether each document is in the topic or not
    labels_mask = topic[0][:, topic[1]]
    num_articles = labels_mask.sum()
    percent_by_source = [float(len(df.loc[(labels_mask) & (df['source'] == outlet)])) / num_articles for outlet in zip(*outlets)[0]]
    normalized = [percent / np.sum(df['source'] == outlet) for percent, outlet in zip(percent_by_source, zip(*outlets)[0])]
    normalized = [percent / np.sum(normalized) for percent in normalized]

    plt.title('Number of Articles in Topic: {}'.format(num_articles), x=0.4825)

    ''' You should incorporate the word_cloud function in here!!! '''
    if not positivity:
        ax2 = fig.add_axes([0.025, 0, 0.79, 0.43])
        wc = WordCloud(background_color='white', max_words=max_words, width=1900, height=625)
    else:
        num_sources = 0
        for idx in xrange(len(outlets)):
            if len(df.loc[(labels_mask) & (df['source'] == outlets[idx][0])]) >= 5:
                num_sources += 1
        ax2 = fig.add_axes([0.025, 0, 0.712125-(num_sources*0.034425), 0.43])
        wc = WordCloud(background_color='white', max_words=max_words, width=1715-(num_sources*83), height=625)
        ax4 = fig.add_axes([0.782125-(num_sources*0.034425), 0.035, 0.034425+(num_sources*0.034425), 0.375])
    word_freq = topic_word_freq(nmf.components_, topic[1], feature_names)
    wc.fit_words(word_freq)
    ax2.imshow(wc)
    ax2.axis('off')
    ax3 = fig.add_axes([0.825, 0.01, 0.15555, 0.4])
    normalized_source_barchart(df, topic, outlets, ax3)
    if positivity:
        sentiment_source_barchart(df.loc[labels_mask], outlets, ax=ax4)
        if num_sources < 3:
            ax4.set_title('')
    if show:
        plt.show()
    return ax1


def normalized_source_barchart(df, topic, outlets, ax=None):
    labels_mask = topic[0][:, topic[1]]
    num_articles = labels_mask.sum()
    percent_by_source = [float(len(df.loc[(labels_mask) & (df['source'] == outlet)])) / num_articles for outlet in zip(*outlets)[0]]
    normalized = [percent / np.sum(df['source'] == outlet) for percent, outlet in zip(percent_by_source, zip(*outlets)[0])]
    normalized = [percent / np.sum(normalized) for percent in normalized]

    if not ax:
        fig, ax = plt.subplots(1, figsize=(2.5,5))
    for idx, percent in enumerate(normalized):
        plt.bar(0, percent, width=1, label=outlets[idx][1], color=outlets[idx][2], bottom=np.sum(normalized[:idx]))
        if percent >= 0.1:
            plt.text(0.5, np.sum(normalized[:idx]) + 0.5*percent, outlets[idx][1] + ': {0:.1f}%'.format(100*percent), horizontalalignment='center', verticalalignment='center')
        elif percent >= 0.05:
            plt.text(0.5, np.sum(normalized[:idx]) + 0.5*percent, outlets[idx][1] + ': {0:.1f}%'.format(100*percent), horizontalalignment='center', verticalalignment='center', fontsize=10)
        elif percent >= 0.025:
            plt.text(0.5, np.sum(normalized[:idx]) + 0.5*percent, outlets[idx][1] + ': {0:.1f}%'.format(100*percent), horizontalalignment='center', verticalalignment='center', fontsize=8)
    plt.axis('off')
    plt.title('% Reported By Source (Normalized)', fontsize=10)


def sentiment_source_barchart(df, outlets, ax=None):
    '''
    INPUT: df - Dataframe containing positivity data for each article.  Can be the entire dataframe or a slice of the dataframe
           outlets - List containing the labels for each outlet and the proper color code for each bar
           ax - Pyplot Axis object.  If None, a figure and axis object will be created, otherwise the barchart will be added to whatever axis object was passed.
    '''
    if not ax:
        fig, ax = plt.subplots(1, figsize=(6, 6))

    # Only include a source if they have at least 5 articles in the df
    idxs = []
    for idx in xrange(len(outlets)):
        if len(df.loc[df['source'] == outlets[idx][0]]) >= 5:
            idxs.append(idx)
    mod_outlets = np.array(outlets)[idxs]

    positivity = [np.mean(df.loc[df['source'] == outlet, 'positive']) for outlet in zip(*mod_outlets)[0]]
    ind = np.arange(len(mod_outlets))  # x locations for each bar
    width = 1.0  # Width of the bars
    colors = zip(*mod_outlets)[2]

    # Create each bar
    rects = ax.bar(ind, positivity, width, color=colors)

    # Set y axis limits
    ax.set_ylim((0.0, 0.9))
    # Add text for labels
    ax.set_xticks(ind + (width/2))
    ax.set_xticklabels(zip(*mod_outlets)[1])
    ax.set_title('Positivity By News Outlet', fontsize=10)
    ax.set_ylabel('% Articles Classified As Positive')
    # Move labels closer to the axis
    ax.xaxis.set_tick_params(pad=4)


def candidate_plots(df, labels, topic_labels, candidate_labels, title, byline=None, freq='W', show=True):
    fig = plt.figure(figsize=(14, 8))
    fig.text(0.05, 0.03, 'Author: Erich Wellinger', fontsize=10, alpha=0.7)
    fig.text(0.33, 0.75, 'github.com/ewellinger/election_analysis', fontsize=20, color='gray', alpha=0.5)
    for candidate in candidate_labels:
        article_count_by_time(df, topic=(labels, candidate), freq=freq, show=False, fig=fig, label=topic_labels[candidate], year=True)
    plt.legend(loc='best')
    plt.subplots_adjust(left=0.05, bottom=0.1, right=0.97)
    plt.suptitle(title)
    if byline:
        plt.title(byline, fontsize=10)
    if show:
        plt.show()


def topic_word_cloud(nmf, topic_idx, max_words=300, figsize=(14, 8), width=2400, height=1300, ax=None):
    ''' Create word cloud for a given topic
    INPUT:
        nmf: NMFClustering object
        topic_idx: int
        max_words: int
            Max number of words to encorporate into the word cloud
        figsize: tuple (int, int)
            Size of the figure if an axis isn't passed
        width: int
        height: int
        ax: None or matplotlib axis object
    '''
    wc = WordCloud(background_color='white', max_words=max_words, width=width, height=height)
    word_freq = nmf.topic_word_frequency(topic_idx)

    # Fit the WordCloud object to the specific topics word frequencies
    wc.fit_words(word_freq)

    # Create the matplotlib figure and axis if they weren't passed in
    if not ax:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
    ax.imshow(wc)
    ax.axis('off')


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    # Plot % of articles mentioning candidate accross all news sources
    # plot_candidate_percentages(df, ['Clinton', 'Trump', 'Bush'])

    nmf, X, W, W_percent, labels, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=90, n_features=10000, random_state=1, max_df=0.8, min_df=5)

    outlets = [('nyt', 'NYT', '#4c72b0'), ('foxnews', 'FOX', '#c44e52'), ('npr', 'NPR', '#55a868'), ('guardian', 'GUA', '#8172b2'), ('wsj', 'WSJ', '#ccb974')]

    # predominant_source = print_topic_summary(df, labels, outlets, topic_words)

    # Create a dictionary with the topic labels for creating the plots
    topic_labels = get_topic_labels()

    # path = './topic_plots/'
    # for idx in xrange(90):
    #     # If the topic is junk, skip making the plot
    #     if topic_labels[idx] == 'junk':
    #         print '\n'
    #         continue
    #     print 'Topic {}: {}'.format(str(idx), topic_labels[idx])
    #     print topic_words[idx]
    #     print '\n'
    #
    #     file_name = path + 'topic_{}_cloud_positivity.png'.format(idx)
    #     topic_time_and_cloud(df, (labels, idx), feature_names, nmf, 'Label {}: {}'.format(str(idx), topic_labels[idx]), show=False)
    #     plt.savefig(file_name, dpi=250)
    #     plt.close()
    #
    #     file_name = path + 'topic_{}_cloud.png'.format(idx)
    #     topic_time_and_cloud(df, (labels, idx), feature_names, nmf, 'Label {}: {}'.format(str(idx), topic_labels[idx]), positivity=False, show=False)
    #     plt.savefig(file_name, dpi=250)
    #     plt.close()
    #
    #     file_name = path + 'topic_{}_time_source.png'.format(idx)
    #     fig = plt.figure(figsize=(14, 8.5))
    #     fig.text(0.05, 0.03, 'Author: Erich Wellinger', fontsize=10, alpha=0.7)
    #     fig.text(0.33, 0.75, 'github.com/ewellinger/election_analysis', fontsize=20, color='gray', alpha=0.5)
    #     article_count_by_time(df, topic=(labels, idx), year=True, source=True, fig=fig, show=False)
    #     plt.subplots_adjust(left=0.05, bottom=0.10, right=0.97, top=0.94)
    #     plt.title('')
    #     plt.suptitle('Label {}: {}'.format(str(idx), topic_labels[idx]), fontsize=14)
    #     plt.savefig(file_name, dpi=300)
    #     plt.close()
    #
    #     file_name = path + 'topic_{}_time_source_normalized.png'.format(idx)
    #     fig = plt.figure(figsize=(14, 8.5))
    #     fig.text(0.05, 0.03, 'Author: Erich Wellinger', fontsize=10, alpha=0.7)
    #     fig.text(0.33, 0.75, 'github.com/ewellinger/election_analysis', fontsize=20, color='gray', alpha=0.5)
    #     article_count_by_time(df, topic=(labels, idx), year=True, source=True, fig=fig, normalize=True, show=False)
    #     plt.subplots_adjust(left=0.05, bottom=0.10, right=0.97, top=0.94)
    #     plt.title('')
    #     plt.suptitle('Label {}: {}'.format(str(idx), topic_labels[idx]), fontsize=14)
    #     plt.savefig(file_name, dpi=300)
    #     plt.close()
    #
    # # Create candidate plot for the remaining democratic candidates
    # candidate_plots(df, labels, topic_labels, [82, 5], 'Remaining 2016 Democratic Candidates', byline='As of February 1, 2016', show=False)
    # plt.savefig('./candidate_plots/democrat.png', dpi=350)
    # plt.close()
    #
    # # Create candidate plot for top 5 republican canidates (as of February 1st, 2016)
    # candidate_plots(df, labels, topic_labels, [2, 14, 22, 9, 4], 'Top 5 Polling 2016 Republican Candidates', byline='As of February 1, 2016', show=False)
    # plt.savefig('./candidate_plots/republican.png', dpi=350)
    # plt.close()


    # Make the gun control plot
    ax = topic_time_and_cloud(df, (labels, 12), feature_names, nmf, 'Label {}: {}'.format(12, topic_labels[12]), positivity=False, show=False)
    msdf = create_shootings_df()
    # article_count_by_time(df, topic=(labels, 12), year=True, show=False)
    c_list = sns.color_palette("Set1", n_colors=10).as_hex()
    # idxs = [0, 2, 4, 12, 13, 30, 38]
    # for c_idx, idx in enumerate(idxs):
        # label = '{} {}: {} Killed, {} Injured'.format(idx+1, msdf.loc[idx, 'city_county'], msdf.loc[idx, 'killed'], msdf.loc[idx, 'injured'])
        # ax.axvline(x=msdf.loc[idx, 'date'], label=label, c=c_list[c_idx], lw=3, alpha=0.8)

    for idx in xrange(5):
        label = '{}: {} ({} Killed, {} Injured)'.format(idx+1, msdf.loc[idx, 'city_county'], msdf.loc[idx, 'killed'], msdf.loc[idx, 'injured'])
        ax.axvline(x=msdf.loc[idx, 'date'], label=label, c=c_list[idx], lw=3, alpha=0.8)
    ax.legend(loc='best')
    plt.savefig('plots/Gun_Control2.png', dpi=300)
