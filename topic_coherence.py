import pandas as pd
import numpy as np
from cluster import nmf_articles
from itertools import permutations
from progressbar import ProgressBar, Percentage
import matplotlib.pyplot as plt
import seaborn as sns


def get_avg_coherence(df, n_topics):
    print '{} Topics Processing...'.format(n_topics)
    nmf, X, W, W_percent, labels, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=n_topics, n_features=10000, random_state=1, max_df=0.8, min_df=5)
    print 'Factorizing Done...'
    pbar = ProgressBar()
    coherence = []
    for words in pbar(topic_words):
        coherence.append(topic_coherence(X, reverse_lookup, words))
    print '\n'
    return np.mean(coherence)


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


def make_coherence_plot(n_topics, coherence, show=False):
    fig = plt.figure(figsize=(12, 8))
    plt.plot(n_topics, coherence)
    plt.xlabel('Number of Topics')
    plt.ylabel('Avg Coherence Score')
    plt.suptitle('Average Coherence Score Among Topics', fontsize=18)
    plt.subplots_adjust(left=0.08, bottom=0.09, right=0.95, top=0.91, hspace=0.16)
    if show:
        plt.show()
    else:
        plt.savefig('./plots/nmf_coherence.png', dpi=350)


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    num_topics = range(2, 31, 2) + range(35, 101, 5) + range(110, 201, 10) + range(225, 401, 25)

    avg_coherence = [get_avg_coherence(df, n_topic) for n_topic in num_topics]

    make_coherence_plot(num_topics, avg_coherence)

# topics = range(2, 31, 2) + range(35, 101, 5) + range(110, 201, 10) + range(225, 401, 25)
# avg_coherence = [-74.949694804000032,
#  -79.499050543893304,
#  -83.20766537930065,
#  -88.350138020815962,
#  -90.806811290179454,
#  -88.966148457213947,
#  -92.259849347336086,
#  -93.693694511355105,
#  -96.229715459278808,
#  -101.02106266796712,
#  -105.26140489793111,
#  -106.44992830555778,
#  -111.19900256168015,
#  -108.3888383643815,
#  -110.42210903014306,
#  -113.06946716707321,
#  -114.56167197849281,
#  -116.51518854832943,
#  -120.75116955758651,
#  -122.07414946308113,
#  -122.73389201912455,
#  -123.20835369178577,
#  -124.4706818825221,
#  -125.2930064826773,
#  -126.67173047873919,
#  -126.11364157215765,
#  -126.91972720705586,
#  -127.58764173111905,
#  -130.76500367061993,
#  -133.18690997621755,
#  -144.88052698246312,
#  -156.09331805752294,
#  -192.39619162591814,
#  -193.04223270498383,
#  -228.03546894957145,
#  -254.53502103391168,
#  -286.54564970701426,
#  -294.97466219245791,
#  -320.66635603102822,
#  -365.14886227907732,
#  -397.78072283424865,
#  -421.15376018755478,
#  -440.271437412821,
#  -465.41217065103001,
#  -472.07237254507726,
#  -490.61559381230097,
#  -499.6807662116052]
