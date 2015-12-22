import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
import nimfa
from load_data import stop_words
from itertools import permutations


def top_words(clusters, feature_names, num_words):
    idxs = [np.argsort(cluster)[-num_words:][::-1] for cluster in clusters]
    return [feature_names[idx] for idx in idxs]


def cluster_headlines(df, labels, kmeans, num_rows=None, random=False):
    '''
    You should probably get rid of this function...
    '''
    if num_rows:
        if random:
            idxs = [np.random.choice(df.loc[labels == label, :].index, size=num_rows) for label in xrange(kmeans.n_clusters)]
            return [df.loc[idx, 'headline'] for idx in idxs]
        else:
            return [df.loc[labels == label, 'headline'][:num_rows] for label in xrange(kmeans.n_clusters)]
    else:
        return [df.loc[labels == label, 'headline'] for label in xrange(kmeans.n_clusters)]


def create_document_vector(df, max_features=5000, max_df=1, min_df=1):
    '''
    INPUTS: df - df['lemmatized_text'] will be what is vectorized
            max_features - number of words to be kept in the TfidfVector
            max_df - Cut off for words appearing in a given threshold of documents. (i.e. 1 = no limit, 0.95 will exclude words appearing in at least 95% of documents from being included in the resulting vector)
            min_df - Cut off for words appearing in a minimum number of documents. (i.e. 2 = term must appear in at least two documents)
    OUTPUT: TfidfVectorizer Object
            TfidfVector
            Feature Names Array
    '''
    stopwords = stop_words()
    # Create TfidfVectorizer
    tfid = TfidfVectorizer(input='content', stop_words=stopwords, use_idf=True, lowercase=True, max_features=max_features)
    X = tfid.fit_transform(df['lemmatized_text'].values)
    feature_names = np.array(tfid.get_feature_names())
    reverse_lookup = {word: idx for idx, word in enumerate(feature_names)}
    return tfid, X, feature_names, reverse_lookup


def cluster_articles(df, n_clusters, max_features=5000, max_df=1, min_df=1,  num_words=15, num_headlines=None):
    tfid, X, feature_names = create_document_vector(df, max_features=max_features, max_df=max_df, min_df=min_df)
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)
    clusters = kmeans.cluster_centers_
    labels = kmeans.labels_
    words = top_words(clusters, feature_names, num_words=num_words)
    headlines = cluster_headlines(df, labels, kmeans, num_rows=num_headlines, random=True)
    return tfid, kmeans, labels, words, headlines


def nmf_articles(df, n_topics, n_features=5000, n_top_words=20, random_state=None, max_df=1, min_df=1):
    tfid, X, feature_names, reverse_lookup = create_document_vector(df, max_features=n_features, max_df=max_df, min_df=min_df)

    nmf = NMF(n_components=n_topics, random_state=random_state, alpha=.1, l1_ratio=0.5).fit(X)
    W = nmf.transform(X)

    labels = np.array([np.argmax(row) for row in W])
    # rel_importance will give a sense of how well a article can be attributed to a given topic
    rel_importance = np.array([row[np.argmax(row)] / row.sum() for row in W])
    words = top_words(nmf.components_, feature_names, n_top_words)

    return tfid, nmf, X, W, labels, rel_importance, words, feature_names, reverse_lookup


def topic_coherence(X, reverse_lookup, topic_words, e=0.01, num_top_words=10):
    '''
    Using the UMass topic coherence as definied in http://anthology.aclweb.org/D/D12/D12-1087.pdf
    '''
    if not num_top_words:
        num_top_words = len(topic_words)
    result = 0.0
    perm = permutations(topic_words[:num_top_words], 2)
    while True:
        try:
            word1, word2 = perm.next()
            result += coherence_score(X, reverse_lookup, word1, word2, e)
        except:
            return result


def coherence_score(X, reverse_lookup, word1, word2, e):
    # return np.log((len(df[df['lemmatized_text'].str.contains(word1) & df['lemmatized_text'].str.contains(word2)]) + e) / df['lemmatized_text'].str.contains(word2).sum())
    return np.log((document_word_count(X, reverse_lookup, word1, word2) + e) / document_word_count(X, reverse_lookup, word2))


def document_word_count(X, reverse_lookup, word1, word2=None):
    '''
    INPUTS: X - tfidf matrix
            reverse_lookup - Dictionary relating word to the cooresponding column in the tfidf matrix
            word1 - First word to search for
            word2 - Second word to search for.
    OUTPUT: Int - Number of documents in the corpus that have either word1 or word1 AND word2
    '''
    if word2:
        return len(np.where((X[:, reverse_lookup[word1]] > 0).toarray() & (X[:, reverse_lookup[word2]] > 0).toarray())[0])
    else:
        return len(np.where((X[:, reverse_lookup[word1]] > 0).toarray())[0])


def sum_squared_err(nmf, X, labels):
    return np.sum([np.linalg.norm(X[idx] - nmf.components_[labels[idx]])**2 for idx in xrange(len(X))])


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    # tfid, kmeans, labels, top_words, headlines = cluster_articles(df, n_clusters=14, max_features=15000, num_words=20, max_df=0.95, min_df=2)

    # tfid, nmf, X, W, labels, rel_importance, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=20, n_features=15000, random_state=1, max_df=0.95, min_df=2)
    # print 'Clustering Done...'
    # coherence = []
    # for idx, words in enumerate(topic_words):
    #     num_articles = len(labels[labels == idx])
    #     mean_purity = rel_importance[labels == idx].mean()
    #     std_purity = rel_importance[labels == idx].std()
    #     print 'Label {}'.format(idx)
    #     print words
    #     print 'Number of articles in topic: {}'.format(num_articles)
    #     print 'Mean Purity: {}'.format(mean_purity)
    #     print 'Std Purity: {}'.format(std_purity)
    #     print 'Normalized Purity: {}'.format(mean_purity / std_purity)
    #     coherence.append(topic_coherence(df, words))
    #     print 'Topic Coherence: {}'.format(coherence[idx])
    #     print '\n'
    # print np.mean(coherence)

    '''
    I'm going to try looking over many different number of latent topics and see what that does to the average topic coherence for each model.
    '''
    avg_coherence = []
    n_topics = range(5, 50, 5)
    for n_topic in n_topics:
        print '{} Topics Processing...'.format(n_topic)
        tfid, nmf, X, W, labels, rel_importance, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=n_topic, n_features=15000, random_state=1, max_df=0.95, min_df=2)
        print 'Factorizing Done...'
        coherence = []
        for words in topic_words:
            coherence.append(topic_coherence(X, reverse_lookup, words))
        avg_coherence.append(np.mean(coherence))
        print 'Avg Coherence Done...\n'


# Topics 12 through 180
# topics = range(12, 51) + range(52, 81, 2) + range(85, 131, 5) + range(140, 181, 10)
# avg_coherence = [-84.271885872677089,
#  -85.056773895715168,
#  -87.207059792746008,
#  -91.283108150538908,
#  -89.059628926444248,
#  -91.46036413392369,
#  -91.550035822549248,
#  -93.139844012185804,
#  -91.925732728396525,
#  -94.358775033486495,
#  -96.502742506711556,
#  -99.034741565714825,
#  -98.702254274317454,
#  -97.888423898130767,
#  -102.34395794737331,
#  -103.28015262557012,
#  -101.2634091458153,
#  -100.66480423304868,
#  -103.58547924985452,
#  -106.11057939146643,
#  -103.16565988091494,
#  -105.35513697221467,
#  -104.70601108947588,
#  -105.75473662540017,
#  -106.41060258426161,
#  -107.63233743517524,
#  -108.74751978047732,
#  -107.464707449849,
#  -108.48114425809096,
#  -109.49846022549401,
#  -111.96143447802491,
#  -113.19636727001493,
#  -112.57067058821157,
#  -110.03253093124079,
#  -113.41379511011189,
#  -112.62906674255117,
#  -112.87709413012958,
#  -115.2142664806567,
#  -115.40772103489027,
#  -116.78368387828597,
#  -114.86973907533985,
#  -116.97142224663536,
#  -117.62904294595,
#  -117.98007215098878,
#  -118.89041999425125,
#  -117.72868611106972,
#  -116.63255904999869,
#  -119.49797922388851,
#  -119.44894180227961,
#  -121.32148328790004,
#  -120.26321591188591,
#  -118.58180592403561,
#  -122.11598722751644,
#  -122.53031004443876,
#  -121.82856623908583,
#  -123.21921697489067,
#  -123.6055355024322,
#  -126.65551586482486,
#  -125.8272888476405,
#  -128.88429861511943,
#  -138.92294342345417,
#  -140.28479208979368,
#  -144.14415983182496,
#  -150.9131725691125,
#  -185.53675513797452,
#  -186.45098435435264,
#  -219.04478511586885,
#  -244.31768424636127,
#  -274.81272634049697]
