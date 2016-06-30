import pandas as pd
import numpy as np
from datetime import date
import matplotlib.pyplot as plt
from PIL import Image
from NMF_Clustering import NMFClustering
from wordcloud import WordCloud, ImageColorGenerator
from scipy.misc import imread
from scrapers.load_data import get_topic_labels
plt.style.use('ggplot')


class ElectionPlotting(object):

    def __init__(self, df, nmf=None, num_topics=None, figsize=(14,8)):
        ''' init docstring
        INPUT:
            df:
            nmf:
            num_topics:
        Explain how it works if you don't pass an nmf object
        '''
        self.df = df
        if isinstance(nmf, NMFClustering):
            # Check to make sure that the object has been fit to the data
            if not hasattr(nmf, 'W_matrix'):
                nmf.fit(df)
            self.nmf = nmf
        elif num_topics:
            self.nmf = NMFClustering(num_topics)
            self.nmf.fit(df)
        else:
            raise ValueError("You must either supply a NMFClustering object or specify the number of topics!")
        self.labels = get_topic_labels()
        self.outlet_sizes = [len(df.loc[df['source'] == outlet]) for outlet in zip(*self.nmf.outlets)[0]]
        self.frequency = {'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly'}
        self.figsize = figsize


    def article_count_by_time(self, searchterm=None, topic_num=None, source=False, freq='W', normalize=False, marker='o', year=False, fig=None, legend_label=None):
        if isinstance(fig, tuple):
            fig = self._create_fig(fig)
        elif not fig:
            fig = self._create_fig

        # If a specific topic was given set the label and subset the dataframe
        if topic_num:
            label = self.labels.get(topic_num, 'Unknown')
            df = self.df.loc[self.nmf.labels[:, topic_num]]
        else:
            df = self.df

        # Subset the dataframe if a searchterm is provided
        if searchterm:
            df = df.loc[df['lemmatized_text'].str.contains(searchterm)]

        # If source is set, split up into a line for each news source
        if source:
            timeseries = [pd.Series([1], index=df.loc[df['source'] == outlet, 'date_published']).resample(freq).sum().fillna(0) for outlet in zip(*self.nmf.outlets)[0]]
            if normalize:
                timeseries = [ts / outlet_size for ts, outlet_size in zip(timeseries, self.outlet_sizes)]
                plt.ylabel('Article Frequency (freq = {})'.format(freq), fontsize=12)
            else:
                plt.ylabel('Article Count (Freq = {})'.format(freq), fontsize=12)

            # plt.subplots_adjust(left=0.08, bottom=0.12, right=0.95, top=0.92)

            for idx, ts in enumerate(timeseries):
                if len(ts):
                    ts.plot(marker=marker, label=self.nmf.outlets[idx][1], c=self.nmf.outlets[idx][2])
            plt.xlabel('Date Published ({})'.format(self.frequency[freq]), fontsize=12)
            plt.legend(loc='best')
        else:
            ts = pd.Series([1], index=df['date_published']).resample(freq).sum().fillna(0)
            if legend_label:
                ts.plot(marker=marker, label=label)
            else:
                ts.plot(marker=marker)
            plt.xlabel('Date Published ({})'.format(self.frequency[freq]), fontsize=12)
            plt.ylabel('Article Count (freq={})'.format(freq), fontsize=12)
        if label:
            plt.title('Topic Number {}: {}'.format(topic_num, label))
        if searchterm:
            plt.title("Articles Containing '{}'".format(searchterm), fontsize=14)
        plt.subplots_adjust(left=0.06, bottom=0.1, right=0.97, top=0.92)


    def _create_fig(self, figsize=None):
        if figsize == None:
            figsize = self.figsize

        fig = plt.figure(figsize=figsize)
        fig.text(0.05, 0.03, 'Author: Erich Wellinger', fontsize=10, alpha=0.7)
        fig.text(0.33, 0.75, 'github.com/ewellinger/election_analysis', fontsize=20, color='gray', alpha=0.5)
        return fig


    def candidate_plots(self, candidate_topic_idxs, title, byline=None, freq='W', fig=None):
        ''' candidate_plots plots multiple topics on one plot
        candidate_topic_idxs: list of int
            Should be a list of int specifying which topic_num to plot
        title: str
            Title for the plot
        byline: str
            Byline to go beneath the title
        '''
        if isinstance(fig, tuple):
            fig = self._create_fig(fig)
        elif not fig:
            fig = self._create_fig()

        for candidate in candidate_topic_idxs:
            self.article_count_by_time(topic_num=candidate, freq=freq, legend_label=self.labels.get(candidate, 'Unknown'), fig=fig, year=True)
        plt.legend(loc='best')
        plt.subplots_adjust(left=0.05, bottom=0.1, right=0.97)
        plt.suptitle(title)
        if byline:
            plt.title(byline, fontsize=10)


    def topic_word_cloud(self, topic_num, max_words=300, figsize=None, width=2400, height=1300, ax=None, mask_fname=None, inherit_color=False):
        ''' Create word cloud for a given topic
        INPUT:
            topic_idx: int
            max_words: int
                Max number of words to encorporate into the word cloud
            figsize: tuple (int, int)
                Size of the figure if an axis isn't passed
            width: int
            height: int
            ax: None or matplotlib axis object
            mask_fname: None or str
                None if no mask is desired, otherwise a string providing the path the image being used as the mask
            inherit_color: bool, default False
                Indicates whether the wordcloud should inherit the colors from the image mask
        '''
        if figsize == None:
            figsize = self.figsize

        if mask_fname:
            mask = np.array(Image.open(mask_fname))
            wc = WordCloud(background_color='white', max_words=max_words, mask=mask, width=width, height=height)
        else:
            wc = WordCloud(background_color='white', max_words=max_words, width=width, height=height)
        word_freq = self.nmf.topic_word_frequency(topic_num)

        # Fit the WordCloud object to the specific topic's word frequencies
        wc.fit_words(word_freq)

        # Create the matplotlib figure and axis if they weren't passed in
        if not ax:
            fig = plt.figure(figsize=self.figsize)
            ax = fig.add_subplot(111)

        if mask_fname and inherit_color:
            image_colors = ImageColorGenerator(imread(mask_fname))
            plt.imshow(wc.recolor(color_func=image_colors))
            plt.axis('off')
        else:
            ax.imshow(wc)
            ax.axis('off')


    def normalized_source_barchart(self):
        pass


    def topic_time_and_cloud(self):
        pass



if __name__=='__main__':
    df = pd.read_pickle('election_data.pkl')

    nmf = NMFClustering(250)
    nmf.fit(df)

    ep = ElectionPlotting(df, nmf)

    # Plot a general plot of all the articles over time
    # ep.article_count_by_time()
    # plt.show()

    # Plot all the articles split up by source over time
    # ep.article_count_by_time(source=True)
    # plt.show()
