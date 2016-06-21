import pandas as pd
import numpy as np
from NMF_Clustering import NMFClustering
from sklearn.decomposition import PCA


def make_skree_plot(pca, n_components, x=None, save=False):
    fig = plt.figure(figsize=(12, 8))
    plt.plot(range(n_components), pca.explained_variance_ratio_[:n_components])
    plt.xlabel('Number of Components')
    plt.ylabel('% Explained Variance')
    if x:
        plt.axvline(x=x, color='r', linestyle='--')
    plt.title('Scree Plot')
    plt.subplots_adjust(left=0.08, bottom=0.08, right=0.96, top=0.93)
    if save:
        plt.savefig('./plots/scree_plot.png', dpi=300)
        plt.close()


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    nmf = NMFClustering(300)
    nmf.fit_tfidf(df)

    pca = PCA()
    pca.fit(nmf.tfidf_matrix)

    make_skree_plot(pca, 300, x=90, save=True)
