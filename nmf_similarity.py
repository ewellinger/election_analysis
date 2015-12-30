import pandas as pd
import numpy as np
from cluster import nmf_articles
from sklearn.metrics.pairwise import pairwise_distances
from progressbar import ProgressBar
import matplotlib.pyplot as plt
import seaborn as sns


def nmf_similarity(df, num_topics):
    print 'Processing {} Topics...'.format(num_topics)
    tfid, nmf, X, W, labels, rel_importance, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=num_topics, n_features=15000, random_state=1, max_df=0.95, min_df=2)
    print 'Clustering Done...'
    pbar = ProgressBar()
    tfidf_similarity = []
    for topic in pbar(xrange(num_topics)):
        # When looking at high numbers of topics, it is possible for no points to be assigned to that topic, in which case pairwise_distances() will throw an error
        if len(labels[labels == topic]):
            cosine_dist = pairwise_distances(X[labels == topic], metric='cosine', n_jobs=-1)
            idx = np.tril_indices(cosine_dist.shape[0], k=-1)
            tfidf_similarity.append(1 - cosine_dist[idx].mean())
    topic_similarity = pairwise_distances(nmf.components_, metric='cosine', n_jobs=1)
    idx = np.tril_indices(topic_similarity.shape[0], k=-1)
    print '\n'
    return np.mean(tfidf_similarity), 1 - topic_similarity[idx].mean(), nmf.reconstruction_err_


def make_similarity_plot(n_topics, tfidf_similarity, topic_similarity):
    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_subplot(211)
    ax1.plot(n_topics, topic_similarity)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.title('Between Topics', fontsize=11)
    ax2 = fig.add_subplot(212, sharex=ax1)
    plt.plot(n_topics, tfidf_similarity)
    plt.xlabel('Number of Topics')
    ax1.set_ylabel('Avg Cosine Similarity')
    ax2.set_ylabel('Avg Cosine Similarity')
    plt.title('Articles Within Topics', fontsize=11)
    plt.suptitle('Cosine Similarity of NMF Model', fontsize=18, x=0.52)
    plt.subplots_adjust(left=0.09, right=0.95, top=0.87, hspace=0.16)
    plt.savefig('plots/nmf_similarity2.png', dpi=350)


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    n_topics = range(2, 41) + range(42, 101, 2) + range(105, 161, 5)
    similarity = [nmf_similarity(df, n_topic) for n_topic in n_topics]
    tfidf_similarity = np.array(zip(*similarity)[0])
    topic_similarity = np.array(zip(*similarity)[1])
    reconst_err = np.array(zip(*similarity)[2])

    make_similarity_plot(n_topics, tfidf_similarity, topic_similarity)
