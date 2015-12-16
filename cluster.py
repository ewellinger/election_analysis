import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from load_data import stop_words


def top_words(clusters, feature_names, num_words):
    idxs = [np.argsort(cluster)[-num_words:][::-1] for cluster in clusters]
    return [feature_names[idx] for idx in idxs]


def cluster_headlines(df, labels, kmeans, num_rows=None, random=False):
    if num_rows:
        if random:
            idxs = [np.random.choice(df.loc[labels == label, :].index, size=num_rows) for label in xrange(kmeans.n_clusters)]
            return [df.loc[idx, 'headline'] for idx in idxs]
        else:
            return [df.loc[labels == label, 'headline'][:num_rows] for label in xrange(kmeans.n_clusters)]
    else:
        return [df.loc[labels == label, 'headline'] for label in xrange(kmeans.n_clusters)]


def cluster_articles(df, n_clusters, max_features=10000, num_words=15, num_headlines=None):
    stopwords = stop_words()

    # Create TfidfVectorizer
    tfid = TfidfVectorizer(input='content', stop_words=stopwords, use_idf=True, lowercase=True, max_features=max_features)
    X = tfid.fit_transform(df['lemmatized_text'].values)
    feature_names = np.array(tfid.get_feature_names())

    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)
    clusters = kmeans.cluster_centers_
    labels = kmeans.labels_
    words = top_words(clusters, feature_names, num_words=num_words)
    headlines = cluster_headlines(df, labels, kmeans, num_rows=num_headlines, random=True)
    return tfid, kmeans, labels, words, headlines


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    tfid, kmeans, labels, top_words, headlines = cluster_articles(df, n_clusters=11, max_features=20000, num_words=20, num_headlines=20)
