import pandas as pd
import numpy as np
import re, string
from pymongo import MongoClient
from load_data import get_canidate_names_2016, parse_str, stop_words, fix_lemmatized_words
import pattern.en as en


''' Convert date_published attribute to a datetime object within the Mongo shell
This code should be executed in the Mongo Terminal shell
Note: This won't work for wsj so you need to leave that type alone and do the conversion in pandas '''
# var cursor = db.articles.find({'source': {$in: ['foxnews', 'npr', 'guardian', 'nyt']}})
# while (cursor.hasNext()) {
#     var doc = cursor.next();
#     db.articles.update({_id: doc._id}, {$set : {date_published : new Date(doc.date_published)}})
# }
''' Check the count of date_published elements which are now of the datetime type '''
# db.articles.find({'date_published': {$type: 9}}).count()


def read_mongo(tab, query={}, no_id=True):
    # Create cursor out of the table with specific query
    cursor = tab.find(query)

    # Construct the dataframe
    df = pd.DataFrame(list(cursor))

    # Delete the _id column
    if no_id:
        df.drop('_id', axis=1, inplace=True)

    return df


def clean_df(df, columns, keywords, lemmatize_text=True, polarity_threshold=0.1):
    # Remove emails, lower text, and convert to str
    df['article_text'] = df['article_text'].apply(remove_email_nums).apply(parse_str).apply(lambda x: x.lower().strip('advertisement').translate(None, string.punctuation))

    # Filter out any record in dataframe where the article_text doesn't contain any of the keywords
    df = df.loc[df['article_text'].str.contains(keywords), :]

    # Lemmatize article text and calculate sentiment if lemmatize_text is set to True
    if lemmatize_text:
        df['lemmatized_text'] = df['article_text'].apply(lemmatize_article)
        columns.append('lemmatized_text')

        ## This didn't really seem to work all that well so I think I'm going to either drop it entirely or replace it with some other implementatino
        # Use pattern.en.sentiment method for creating columns for polarity, sentiment, and positivity (using polarity_threshold as cutoff between negative/positive)
        # sentiment = df['article_text'].apply(en.sentiment)
        # df['polarity'] = zip(*sentiment)[0]
        # df['subjectivity'] = zip(*sentiment)[1]
        # df['positive'] = df['polarity'] >= polarity_threshold
        # columns.append('polarity')
        # columns.append('subjectivity')
        # columns.append('positive')

    # Remove duplicate entrys
    df = df.drop_duplicates('url')

    # Fox News seems to reprint some articles multiple times with different URLs but the same headline so we want to remove these from the dateset
    df = df.drop_duplicates('headline')

    # Sort by the date_published and reset the index
    df = df.sort_values(by='date_published').reset_index(drop=True)

    # Reorder / drop columns
    return df[columns]


def remove_email_nums(doc):
    # Remove any numbers from article text
    doc = re.sub(r'[0-9]', '', doc)
    # Return article text with any email addresses removed
    return re.sub(r'[\w\.-]+@[\w\.-]+', '', doc)


def lemmatize_article(article):
    '''
    INPUT: article (str) - raw text from the article (where text has been lowered and punctuation removed already)
    OUTPUT: lemmatized_article - article text with all stopwords removed and the remaining text lemmatized
    '''
    # Load in stopwords from load_data
    stopwords = stop_words()
    # Load Dictionary to fix commonly mislemmatized words
    correct_lemma = fix_lemmatized_words()
    # Lemmatize article by running each word through the pattern.en lemmatizer and only including it in the resulting text if the word doesn't appear in the set of stopwords
    article = ' '.join([en.lemma(w) for w in article.split() if w not in stopwords])
    # Return the article text after fixing common mislemmatized words
    return ' '.join([correct_lemma[w] if w in correct_lemma else w for w in article.split()])


if __name__=='__main__':
    # Create MongoClient
    client = MongoClient()
    # Initialize the Database
    db = client['election_analysis']
    # Initialize table
    tab = db['articles']

    keywords = get_canidate_names_2016()

    # Columns to keep in the resulting dataframe
    columns = ['date_published', 'source', 'url', 'author', 'content_type', 'headline', 'article_text']

    # Read in the data from the Mongo database and return a pandas dataframe of the resulting information
    df = read_mongo(tab)

    # Process the dataframe
    df = clean_df(df, columns, keywords)

    # Save the pickled dataframe for easy access later
    df.to_pickle('./election_data.pkl')
