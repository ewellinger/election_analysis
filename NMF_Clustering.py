import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from scrapers.load_data import stop_words
import cPickle as pickle


class NMFClustering(object):
    def __init__(self, num_topics, tfidf_max_features=5000, tfidf_max_df=0.75, tfidf_min_df=20, nmf_alpha=0.1, nmf_l1_ratio=0.25, random_state=42):
        ''' init docstring
            Stuff and things
        '''
        if isinstance(num_topics, (int, float)):
            self.num_topics = int(num_topics)
        else:
            raise ValueError('num_topics must be an int')
        self.tfidf_max_features = tfidf_max_features
        self.tfidf_max_df = tfidf_max_df
        self.tfidf_min_df = tfidf_min_df
        self.nmf_alpha = nmf_alpha
        self.nmf_l1_ratio = nmf_l1_ratio
        self.random_state = random_state
        self.stop_words = stop_words()
        self.outlets = [('nyt', 'NYT', '#4c72b0'), ('foxnews', 'FOX', '#c44e52'), ('npr', 'NPR', '#55a868'), ('guardian', 'GUA', '#8172b2'), ('wsj', 'WSJ', '#ccb974')]


    def fit(self, df):
        ''' Run NMF on the given Dataframe
        INPUT:
            df: Dataframe
                Dataframe with a column 'lemmatized_text' which is what will be vectorized.
        '''
        # Create our TFIDF matrix
        self.fit_tfidf(df)

        # Create the NMF object and fit it to the tfidf matrix
        self.nmf = NMF(n_components=self.num_topics, alpha=self.nmf_alpha, l1_ratio=self.nmf_l1_ratio, random_state=self.random_state).fit(self.tfidf_matrix)

        # Create the W matrix
        self.W_matrix = self.nmf.transform(self.tfidf_matrix)

        # Currently the attribution for each row in W is not a percentage, but we want to assign each document to any topic which it can be at least 10% attributed to
        sums = np.sum(self.W_matrix, axis=1)
        self.W_percent = self.W_matrix / sums[:, None]

        # For efficient slicing we will save a sparse boolean array indicating if a given article is at least 5% attributable to a particular topic or not
        self.labels = self.W_percent >= 0.05


    def fit_tfidf(self, df):
        ''' Create a TFIDF matrix using the given dataframe
        INPUT:
            df: Pandas Dataframe
                Dataframe with a column 'lemmatized_text' which is what the TFIDF matrix will be created from
        '''
        # First create the Tfidf object and save it as an attribute
        self.tfidf = TfidfVectorizer(input='content', stop_words=self.stop_words, use_idf=True, lowercase=True, max_features=self.tfidf_max_features, max_df=self.tfidf_max_df, min_df=self.tfidf_min_df)

        # Create the tfidf matrix using the lemmatized text
        self.tfidf_matrix = self.tfidf.fit_transform(df['lemmatized_text'].values).toarray()

        # Save the feature names and a reverse lookup for quickly returning the index of a given word in the feature names array
        self.tfidf_feature_names = np.array(self.tfidf.get_feature_names())
        self.tfidf_reverse_lookup = {word: idx for idx, word in enumerate(self.tfidf_feature_names)}


    def top_words_by_topic(self, n_top_words, topic=None):
        '''
        Want to get the indicies of the top given number of words broken down by each topic
        Maybe rever to the self.tfidf_features_names directly to just output the words?
        Have an optional input for only giving the words for a particular cluster or getting all of them
        '''
        if topic != None:
            idx = np.argsort(self.nmf.components_[topic])[-n_top_words:][::-1]
            return self.tfidf_feature_names[idx]
        else:
            idxs = [np.argsort(topic)[-n_top_words:][::-1] for topic in self.nmf.components_]
            return np.array([self.tfidf_feature_names[idx] for idx in idxs])


    def topic_attribution_by_document(self, document_idx):
        ''' Return array of (topic_number, % attribution) for document
        INPUT:
            document_idx: int
                Which document in the corpus you'd like the breakdown of topics for.
        OUTPUT:
            Array of tuples consisting of (topic_num, % attribution) sorted in descending order
        '''
        idxs = np.where(self.labels[document_idx] == 1)[0]
        idxs = idxs[np.argsort(self.W_percent[document_idx, idxs])[::-1]]
        return np.array([(idx, percent) for idx, percent in zip(idxs, self.W_percent[document_idx, idxs])])


    def print_topic_summary(self, df, topic_num, num_words=20):
        ''' Print a summary for a given topic number
        INPUT:
            topic_num: int
        OUTPUT:
            Will print out the number of articles in the topic as well as the breakdown of the percentage of articles printed by each outlet and a breakdown normalized by how many articles that outlet has published in the corpus
        '''
        num_articles = self.labels[:, topic_num].sum()
        print 'Summary of Topic {}:'.format(topic_num)
        print 'Number of articles in topic: {}'.format(num_articles)
        print 'Top {} words in topic:'.format(num_words)
        print self.top_words_by_topic(num_words, topic_num)
        if not num_articles:
            return None
        articles_by_source = [float(len(df.loc[(self.labels[:, topic_num]) & (df['source'] == outlet)])) / num_articles for outlet in zip(*self.outlets)[0]]
        print 'Breakdown by source:'
        print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*self.outlets)[1], articles_by_source)])

        normalized = [percent / len(df.loc[df['source'] == outlet]) for outlet, percent in zip(zip(*self.outlets)[0], articles_by_source)]
        normalized = [percent / np.sum(normalized) for percent in normalized]

        print 'Breakdown normalized by number of articles published by source:'
        print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*self.outlets)[1], normalized)])


    def topic_word_frequency(self, topic_idx):
        ''' Return (word, frequency) tuples for creating word cloud
        INPUT:
            topic_idx: int
        '''
        freq_sum = np.sum(self.nmf.components_[topic_idx])
        frequencies = [val / freq_sum for val in self.nmf.components_[topic_idx]]
        return zip(self.tfidf_feature_names, frequencies)


if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')
    nmf = NMFClustering(250)
    nmf.fit(df)

    # Print a summary of the first topic
    # nmf.print_topic_summary(df, 0)

    with open('NMFClusteringObj.pkl', 'w') as f:
        pickle.dump(nmf, f)
