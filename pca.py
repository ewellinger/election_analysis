import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib
from cycler import cycler
from NMF_Clustering import NMFClustering

# Set style options
plt.style.use('ggplot')
color_cycle = cycler(color=['#4c72b0', '#55a868', '#c44e52', '#8172b2', '#ccb974', '#64b5cd'])
matplotlib.rcParams['axes.prop_cycle'] = color_cycle
matplotlib.rcParams['lines.linewidth'] = 1.75


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

    nmf = NMFClustering(-1)
    nmf.fit_tfidf(df)

    pca = PCA()
    pca.fit(nmf.tfidf_matrix)

    make_skree_plot(pca, 350, x=250, save=True)
