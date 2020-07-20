import os
from datetime import datetime
from dateutil.parser import parse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition
from textblob import TextBlob
from scripts.preprocess_text import preprocess

# initialize datetime
date = datetime.now().strftime("%d_%b_%Y")


def convert_datetime(text: str) -> str:
    """Replace date format June 06, 2020 to 2020-06-06"""
    try:
        return str(parse(text).date())
    except Exception as ex:
        print(ex)
        return ""


def merge_csv_files(directory: str, pattern=".csv") -> pd.DataFrame():

    # Initialize DataFrame
    df = pd.DataFrame()

    for folder in os.listdir(directory):
        if folder.endswith('2020'):
            # List all files in this directory
            folder = os.path.join(directory, folder)
            for root, _, files in os.walk(folder):
                for basename in files:
                    if basename.endswith(pattern):
                        filename = os.path.join(root, basename)
                        print(filename)
                        csv_df = pd.read_csv(filename, header=None, names=[
                                             'link', 'header', 'article', 'author', 'date'])
                        csv_df['source'] = filename.replace(
                            'raw_data/', '')[:3]
                        # Merge all CSV files
                        df = pd.concat([csv_df, df], ignore_index=False)

    return df


def sentiment_score(text: str) -> int:
    wiki = TextBlob(text)
    numberOfSentences = 0
    score = 0
    for sentence in wiki.sentences:
        polarity = sentence.sentiment.polarity
        subjectivity = sentence.sentiment.subjectivity
        numberOfSentences += 1
        score += polarity * subjectivity

    if numberOfSentences < 1:
        normalized_score = round(score, 3)
    else:
        normalized_score = round(score / numberOfSentences, 3)
    return normalized_score


def sentiment_label(score: int) -> str:
    # Classifying sentence based on score.
    if score > 0:
        sentiment_label = "positive"
    elif score < 0:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    return sentiment_label

NUM_TOPICS = 5
NUM_TOP_WORDS = 5

def topic_extractions(df):
    vectorizer = CountVectorizer(stop_words='english')
    X_train_dtm = vectorizer.fit_transform(df['article'])
    vocab = np.array(vectorizer.get_feature_names())

    # Generating Decomposition Model to extract topics
    clf = decomposition.NMF(n_components=NUM_TOPICS, random_state=1)
    doctopic = clf.fit_transform(X_train_dtm)

    # Generating dominant topics for each words
    topic_words = []
    for topic in clf.components_:
        word_idx = np.argsort(topic)[::-1][0:NUM_TOP_WORDS]
        topic_words.append([vocab[i] for i in word_idx])

    # Making DataFrame that gets the doctopic (values of topics for each text)
    dftopic = pd.DataFrame(doctopic, columns=topic_words)
    dftopicinv = dftopic.T

    # Getting the dominant topic
    topic_series = []
    for i in np.arange(dftopic.shape[0]):
        topic_series.append(dftopicinv[i].idxmax())

    df['toptopic'] = topic_series

    return df

def clean_df(df: pd.DataFrame()) -> pd.DataFrame():
    # Remove the first row of dataframe
    df = df[df['header'] != '']
    # Remove duplicated rows with the same link
    df.drop_duplicates(subset="link", keep=False, inplace=True)
    # Convert time in datetime
    df['date'] = df['date'].apply(lambda text: convert_datetime(text))
    df['header'] = df['header'].apply(lambda text: preprocess(text))
    df['article'] = df['article'].apply(lambda text: preprocess(text))
    df['score'] = df.apply(lambda text: sentiment_score(
        text['header'] + text['article']), axis=1)
    df['label'] = df['score'].apply(lambda text: sentiment_label(text))
    df = topic_extractions(df)

    return df

