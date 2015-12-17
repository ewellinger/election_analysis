import pandas as pd
import numpy as np
import re, string
from pymongo import MongoClient
from load_data import get_canidate_names_2016, parse_str, stop_words
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


def clean_df(df, columns, keywords, lemmatize_text=True):
    # Remove emails, lower text, and convert to str
    df['article_text'] = df['article_text'].apply(remove_email_nums).apply(parse_str).apply(lambda x: x.lower().strip('advertisement').translate(None, string.punctuation))

    # Filter out any record in dataframe where the article_text doesn't contain any of the keywords
    df = df.loc[df['article_text'].str.contains(keywords), :]

    # Lemmatize article text if lemmatize_text is set to True
    if lemmatize_text:
        df['lemmatized_text'] = df['article_text'].apply(lemmatize_article)
        columns.append('lemmatized_text')

    # Sort by the date_published and reset the index
    df = df.sort_values(by='date_published').reset_index(drop=True)

    # Reorder / drop columns
    return df[columns]


def remove_email_nums(doc):
    doc = re.sub(r'[0-9]', '', doc)
    return re.sub(r'[\w\.-]+@[\w\.-]+', '', doc)


def lemmatize_article(article):
    stopwords = stop_words()
    return ' '.join([en.lemma(w) for w in article.split() if w not in stopwords])


if __name__=='__main__':
    # Create MongoClient
    client = MongoClient()
    # Initialize the Database
    db = client['election_analysis']
    # Initialize table
    tab = db['articles']

    keywords = get_canidate_names_2016()
    columns = ['date_published', 'source', 'url', 'author', 'content_type', 'headline', 'article_text']

    df = read_mongo(tab)

    df = clean_df(df, columns, keywords)

    df.to_pickle('./election_data.pkl')
