import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
from load_data import stop_words


def top_words(clusters, feature_names, num_words):
    idxs = [np.argsort(cluster)[-num_words:][::-1] for cluster in clusters]
    return [feature_names[idx] for idx in idxs]


def topic_word_freq(topics, idx, feature_names):
    '''
    INPUT: topics - Array of word values from nmf_components_
           idx - Topic label to return frequencies for
           feature_names - Array of words from tfidf matrix
    OUTPUT: Array of (word, freq) tuples
    '''
    freq_sum = np.sum(topics[idx])
    frequencies = [val / freq_sum for val in topics[idx]]
    return zip(feature_names, frequencies)


def create_document_vector(df, max_features=5000, max_df=1, min_df=1):
    '''
    INPUTS: df - df['lemmatized_text'] will be what is vectorized
            max_features - number of words to be kept in the TfidfVector
            max_df - Cut off for words appearing in a given threshold of documents. (i.e. 1 = no limit, 0.95 will exclude words appearing in at least 95% of documents from being included in the resulting vector)
            min_df - Cut off for words appearing in a minimum number of documents. (i.e. 2 = term must appear in at least two documents)
    OUTPUT: TfidfVector (X)
            Feature Names Array
            Reverse_lookup Dictionary - Used to quickly and efficiently return the index of a given word in the Feature Names Array
    '''
    stopwords = stop_words()
    # Create TfidfVectorizer
    tfid = TfidfVectorizer(input='content', stop_words=stopwords, use_idf=True, lowercase=True, max_features=max_features, max_df=max_df, min_df=min_df)
    X = tfid.fit_transform(df['lemmatized_text'].values)
    feature_names = np.array(tfid.get_feature_names())
    reverse_lookup = {word: idx for idx, word in enumerate(feature_names)}
    return X, feature_names, reverse_lookup


def cluster_articles(df, n_clusters, max_features=5000, max_df=1, min_df=1,  num_words=15):
    X, feature_names = create_document_vector(df, max_features=max_features, max_df=max_df, min_df=min_df)
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)
    clusters = kmeans.cluster_centers_
    labels = kmeans.labels_
    words = top_words(clusters, feature_names, num_words=num_words)
    return tfid, kmeans, labels, words


def nmf_articles(df, n_topics, n_features=5000, n_top_words=20, random_state=None, max_df=1, min_df=1):
    tfidf, feature_names, reverse_lookup = create_document_vector(df, max_features=n_features, max_df=max_df, min_df=min_df)
    nmf = NMF(n_components=n_topics, random_state=random_state, alpha=.1, l1_ratio=0.25).fit(tfidf)
    W = nmf.transform(tfidf)

    # Currently the attribution for each row in W is not a percentage, but we want to assign each document to any topic which it can be at least 10% attributed to
    sums = np.sum(W, axis=1)
    W_percent = W / sums[:, None]

    # For efficient slicing we will return a sparse boolean array
    labels = W_percent >= 0.1

    words = top_words(nmf.components_, feature_names, n_top_words)
    return nmf, tfidf, W, W_percent, labels, words, feature_names, reverse_lookup


def print_topic_summary(df, labels, outlets, topic_words):
    predominant_source = {'NYT': [], 'FOX': [], 'NPR': [], 'GUA': [], 'WSJ': []}
    for idx, words in enumerate(topic_words):
        num_articles = labels[:, idx].sum()
        print 'Label {}'.format(idx)
        print words
        print 'Number of articles in topic: {}'.format(num_articles)
        if not num_articles:
            print '\n'
            continue
        articles_by_source = [float(len(df.loc[(labels[:, idx]) & (df['source'] == outlet)])) / num_articles for outlet in zip(*outlets)[0]]
        print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*outlets)[1], articles_by_source)])
        normalized = [percent / len(df.loc[df['source'] == outlet]) for percent, outlet in zip(articles_by_source, zip(*outlets)[0])]
        normalized = [percent / np.sum(normalized) for percent in normalized]
        for outlet, percent in zip(zip(*outlets)[1], normalized):
            if percent >= 0.35:
                predominant_source[outlet].append((idx, percent))
        print 'Normalized Percentages'
        print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*outlets)[1], normalized)])
        print '\n'
    return predominant_source


def document_topics(doc_num, labels, W_percent):
    '''
    INPUT: doc_num - Which document you would like the topic breakdown for
           labels - label array
           W_percent - Percentage attribution for each topic
    OUTPUT: Array of tuples consisting of (topic_num, % attribution) sorted in decending order
    '''
    idxs = np.where(labels[doc_num] == 1)[0]
    idxs = idxs[np.argsort(W_percent[doc_num, idxs])[::-1]]
    return np.array([(idx, percent) for idx, percent in zip(idxs, W_percent[doc_num, idxs])])


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    nmf, X, W, W_percent, labels, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=90, n_features=10000, random_state=1, max_df=0.8, min_df=5)

    outlets = [('nyt', 'NYT', '#4c72b0'), ('foxnews', 'FOX', '#c44e52'), ('npr', 'NPR', '#55a868'), ('guardian', 'GUA', '#8172b2'), ('wsj', 'WSJ', '#ccb974')]

    predominant_source = print_topic_summary(df, labels, outlets, topic_words)
