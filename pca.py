import pandas as pd
import numpy as np
from cluster import create_document_vector
from sklearn.decomposition import PCA


def make_skree_plot(pca, n_components=180, x=None, save=False):
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
    else:
        plt.show()


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    tfid, X, feature_names, reverse_lookup = create_document_vector(df, max_features=10000, max_df=0.8, min_df=5)

    pca = PCA()
    pca.fit(X)

    make_skree_plot(pca, x=90, save=True)
