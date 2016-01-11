import pandas as pd
import numpy as np
from cluster import nmf_articles
from sklearn.metrics.pairwise import pairwise_distances
from progressbar import ProgressBar
import matplotlib.pyplot as plt
import seaborn as sns


def nmf_similarity(df, num_topics):
    print 'Processing {} Topics...'.format(num_topics)
    tfid, nmf, X, W, labels, topic_words, feature_names, reverse_lookup = nmf_articles(df, n_topics=num_topics, n_features=10000, random_state=1, max_df=0.8, min_df=5)
    print 'Clustering Done...'
    pbar = ProgressBar()
    tfidf_similarity = []
    num_zero = 0
    for topic in pbar(xrange(num_topics)):
        # When looking at high numbers of topics, it is possible for no points to be assigned to that topic, in which case pairwise_distances() will throw an error
        if len(labels[labels == topic]):
            cosine_dist = pairwise_distances(X[labels == topic], metric='cosine', n_jobs=-1)
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

    n_topics = range(2, 41) + range(42, 101, 2) + range(105, 176, 5)
    similarity = [nmf_similarity(df, n_topic) for n_topic in n_topics]
    tfidf_similarity = np.array(zip(*similarity)[0])
    topic_similarity = np.array(zip(*similarity)[1])
    reconst_err = np.array(zip(*similarity)[2])

    make_similarity_plot(n_topics, tfidf_similarity, topic_similarity, x=130)




# n_topics = range(2, 41) + range(42, 101, 2) + range(105, 176, 5)
# tfidf_similarity = [ 0.08407457,  0.10277214,  0.10683644,  0.11559316,  0.1254214 ,
#         0.12658142,  0.1297214 ,  0.1376438 ,  0.13976171,  0.14045832,
#         0.14532574,  0.14889247,  0.15027123,  0.1538476 ,  0.15789083,
#         0.15719911,  0.16025885,  0.16034179,  0.1623843 ,  0.15991305,
#         0.1634971 ,  0.16776071,  0.17101277,  0.16916474,  0.17002996,
#         0.17127685,  0.16945176,  0.17335869,  0.17663525,  0.17446925,
#         0.18547991,  0.17720962,  0.17592041,  0.17791337,  0.17981856,
#         0.18360806,  0.17932908,  0.18190827,  0.18252199,  0.19002579,
#         0.1880875 ,  0.18629158,  0.19734279,  0.20293701,  0.19393961,
#         0.20339409,  0.19318592,  0.20519563,  0.19995049,  0.20995353,
#         0.20668557,  0.21287803,  0.21523493,  0.21691184,  0.21431059,
#         0.20918813,  0.22435478,  0.22316101,  0.22091046,  0.21815225,
#         0.22627881,  0.21991326,  0.22753801,  0.2268084 ,  0.22715958,
#         0.22611947,  0.22631521,  0.22672403,  0.23030202,  0.22872257,
#         0.2346052 ,  0.232749  ,  0.23176857,  0.23592457,  0.23642996,
#         0.2304059 ,  0.23367956,  0.23282773,  0.23583408,  0.23584327,
#         0.23402352,  0.23519194,  0.23593402,  0.23001135]
# topic_similarity = [ 0.41877678,  0.27734438,  0.23603463,  0.23070781,  0.18313996,
#         0.16596814,  0.14531793,  0.15229488,  0.11547263,  0.11955607,
#         0.10615515,  0.09566632,  0.09386856,  0.08383843,  0.07770674,
#         0.07642413,  0.07311248,  0.06581363,  0.06515176,  0.06279139,
#         0.05925459,  0.05761892,  0.05253173,  0.05382539,  0.04938433,
#         0.04678647,  0.04752572,  0.04620386,  0.04455167,  0.04305006,
#         0.04370832,  0.04024443,  0.04340059,  0.04092858,  0.04077606,
#         0.03770718,  0.03867624,  0.03601939,  0.03402122,  0.03451103,
#         0.034186  ,  0.03209286,  0.03279155,  0.0311164 ,  0.02916519,
#         0.02857462,  0.02790113,  0.02722941,  0.02565511,  0.02637374,
#         0.02538705,  0.02295081,  0.02432675,  0.02296878,  0.02154173,
#         0.02130756,  0.02074324,  0.02070282,  0.020045  ,  0.02017545,
#         0.01967953,  0.01832329,  0.01792477,  0.01855725,  0.017499  ,
#         0.01827365,  0.01750623,  0.01724154,  0.01641006,  0.01611956,
#         0.01482381,  0.01428533,  0.01364422,  0.01296166,  0.01232889,
#         0.01223413,  0.0119174 ,  0.01124019,  0.01081575,  0.01053756,
#         0.0099266 ,  0.00933769,  0.00924058,  0.00841562]
