import pandas as pd
import numpy as np
from cluster import nmf_articles
from sklearn.metrics.pairwise import pairwise_distances
from progressbar import ProgressBar
import matplotlib.pyplot as plt
import seaborn as sns


def nmf_similarity(df, num_topics):
    print 'Processing {} Topics...'.format(num_topics)
    nmf, X, W, W_percent, labels, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=num_topics, n_features=10000, random_state=1, max_df=0.8, min_df=5)
    print 'Clustering Done...'
    pbar = ProgressBar()
    tfidf_similarity = []
    num_zero = 0
    for topic in pbar(xrange(num_topics)):
        # When looking at high numbers of topics, it is possible for no points to be assigned to that topic, in which case pairwise_distances() will throw an error.  The label should also be skipped if only one article is assigned as pairwise_distances will return nan
        if labels[:, topic].sum() > 1:
            cosine_dist = pairwise_distances(X[labels[:, topic]], metric='cosine', n_jobs=-1)
            idx = np.tril_indices(cosine_dist.shape[0], k=-1)
            tfidf_similarity.append(1 - cosine_dist[idx].mean())
        else:
            num_zero += 1
    topic_similarity = pairwise_distances(nmf.components_, metric='cosine', n_jobs=1)
    idx = np.tril_indices(topic_similarity.shape[0], k=-1)
    if num_zero:
        print 'Number of Empty Topics: {}'.format(num_zero)
    print '\n'
    return np.mean(tfidf_similarity), 1 - topic_similarity[idx].mean(), nmf.reconstruction_err_


def make_similarity_plot(n_topics, tfidf_similarity, topic_similarity, x=None):
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
    if x:
        ax1.axvline(x=x, color='r', linestyle='--')
        ax2.axvline(x=x, color='r', linestyle='--')
    plt.title('Articles Within Topics', fontsize=11)
    plt.suptitle('Cosine Similarity of NMF Model', fontsize=18, x=0.52)
    plt.subplots_adjust(left=0.09, right=0.95, top=0.87, hspace=0.16)
    plt.savefig('plots/nmf_similarity_2.png', dpi=350)


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    n_topics = range(185, 301, 5) + range(310, 401, 10)
    similarity = [nmf_similarity(df, n_topic) for n_topic in n_topics]
    tfidf_similarity = np.array(zip(*similarity)[0])
    topic_similarity = np.array(zip(*similarity)[1])
    reconst_err = np.array(zip(*similarity)[2])

    make_similarity_plot(n_topics, tfidf_similarity, topic_similarity, x=90)



# n_topics = range(2, 61) + range(62, 181, 2) + range(185, 301, 5) + range(310, 401, 10)
# tfidf_similarity = [ 0.06919003,  0.07716082,  0.07772778,  0.08091129,  0.08144706,
#         0.08441722,  0.08877972,  0.08665998,  0.09185146,  0.09250131,
#         0.09337106,  0.09548613,  0.09502146,  0.09613326,  0.09803448,
#         0.09986896,  0.10113093,  0.09897356,  0.10167923,  0.10179092,
#         0.10168487,  0.10372497,  0.10458561,  0.10525578,  0.10732481,
#         0.10925675,  0.10870148,  0.11037501,  0.11156316,  0.11185519,
#         0.11199085,  0.11281236,  0.11294679,  0.11386732,  0.11423408,
#         0.11498361,  0.11536422,  0.11573757,  0.11792595,  0.11950781,
#         0.11655657,  0.11812634,  0.11947485,  0.11871727,  0.12008633,
#         0.12042659,  0.12230301,  0.12326621,  0.1236972 ,  0.12366165,
#         0.12528701,  0.12642708,  0.12578936,  0.12545484,  0.12782503,
#         0.1272966 ,  0.12887068,  0.12718231,  0.12973078,  0.13107789,
#         0.13057604,  0.1323204 ,  0.13404527,  0.13374308,  0.13589143,
#         0.13821188,  0.13883294,  0.13949307,  0.13993016,  0.14322494,
#         0.14131143,  0.14733956,  0.14674232,  0.14901972,  0.15068091,
#         0.15081911,  0.14525186,  0.15015424,  0.15015982,  0.14821386,
#         0.15484737,  0.15447583,  0.15582123,  0.15171278,  0.15722498,
#         0.15658193,  0.15710339,  0.15770883,  0.15761817,  0.15321364,
#         0.15915902,  0.15628147,  0.15998298,  0.15984414,  0.16126671,
#         0.16272429,  0.16392751,  0.16212226,  0.16335412,  0.16381869,
#         0.16578948,  0.16365815,  0.16559053,  0.16315932,  0.16561612,
#         0.1667905 ,  0.16536796,  0.1657465 ,  0.16807002,  0.17023921,
#         0.16765957,  0.16687815,  0.16767499,  0.16904597,  0.17098611,
#         0.16999126,  0.16940434,  0.170338  ,  0.17302464, 0.17337105,  0.17262931,  0.17346992,  0.1738747 ,  0.17550675,
#         0.17643292,  0.17683679,  0.1793949 ,  0.17928088,  0.18097037,
#         0.17963404,  0.17956181,  0.18138156,  0.18546755,  0.18128459,
#         0.18311943,  0.18586499,  0.18147474,  0.18387541,  0.18350862,
#         0.18475292,  0.18013974,  0.1854419 ,  0.18160179,  0.18323144,
#         0.18409187,  0.18019803,  0.18173809,  0.17943567,  0.17983233,
#         0.1795946 ,  0.18003193,  0.17937496,  0.17901832]
# topic_similarity = [ 0.49139534,  0.32038063,  0.29737638,  0.26290635,  0.21899265,
#         0.18858076,  0.19074131,  0.18503298,  0.15762876,  0.15172506,
#         0.14302446,  0.13138557,  0.12984286,  0.12293455,  0.11003601,
#         0.10311668,  0.09695369,  0.09694434,  0.08780933,  0.08832456,
#         0.08263554,  0.07983522,  0.07709845,  0.07294574,  0.0733138 ,
#         0.06919578,  0.06960932,  0.06555719,  0.06428637,  0.06296457,
#         0.0599141 ,  0.05880432,  0.05918169,  0.05664977,  0.05522813,
#         0.05619417,  0.05302535,  0.05358813,  0.05125477,  0.05010702,
#         0.05130872,  0.04945229,  0.04873649,  0.04987588,  0.04834414,
#         0.04713466,  0.04589051,  0.0476106 ,  0.0450979 ,  0.04463465,
#         0.04213774,  0.04300594,  0.04212631,  0.04198359,  0.03959167,
#         0.04129826,  0.04007058,  0.03815924,  0.0392492 ,  0.03909244,
#         0.0369244 ,  0.0368154 ,  0.03533346,  0.03401247,  0.03396326,
#         0.03361657,  0.03215782,  0.03209619,  0.03194737,  0.03054921,
#         0.03127004,  0.02938689,  0.02912781,  0.02825228,  0.02783441,
#         0.02752382,  0.02730068,  0.02701021,  0.02622771,  0.02613531,
#         0.02520166,  0.02509368,  0.02466549,  0.02363334,  0.02443221,
#         0.0234695 ,  0.02261527,  0.02257537,  0.02272214,  0.02237474,
#         0.02225426,  0.02156303,  0.02111241,  0.02073749,  0.02000515,
#         0.02073796,  0.02030128,  0.01964259,  0.01910732,  0.01895146,
#         0.01883269,  0.01817971,  0.01829162,  0.01744238,  0.01809634,
#         0.01768637,  0.01682432,  0.0174763 ,  0.01690263,  0.01747576,
#         0.01669802,  0.01627276,  0.0164218 ,  0.01585548,  0.01595765,
#         0.01529798,  0.01575638,  0.01533035,  0.01545988, 0.01468853,  0.01450352,  0.01395368,  0.01332298,  0.01323394,
#         0.01277348,  0.01232136,  0.01251358,  0.01192815,  0.01155009,
#         0.01116601,  0.01065091,  0.01027406,  0.01055548,  0.00975815,
#         0.00955649,  0.00975181,  0.00880756,  0.00855269,  0.00847836,
#         0.00833741,  0.0075285 ,  0.00754154,  0.00728213,  0.00680744,
#         0.00654837,  0.00576125,  0.00553734,  0.00506675,  0.00481164,
#         0.00445332,  0.00425512,  0.00384454,  0.00365881]
