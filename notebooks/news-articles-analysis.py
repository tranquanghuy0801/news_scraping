import pandas as pd
import os
import fnmatch
import glob
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from preprocess_text import *
from textblob import TextBlob

def merge_csv_files(directory: str, pattern = "*.csv") -> pd.DataFrame(): 

	# Initialize DataFrame
	df = pd.DataFrame()

	# List all files in this directory 
	for root, dirs, files in os.walk(directory):
		for basename in files:
			if fnmatch.fnmatch(basename, pattern):
				filename = os.path.join(root, basename)
				print(filename)
				csv_df = pd.read_csv(filename,header=None,names=['link','header','article','author','date'])
				# Merge all CSV files
				df = pd.concat([csv_df,df],ignore_index=False)
	
	return df

def sentiment_score(text: str) -> int:
	wiki = TextBlob(text)
	numberOfSentences = 0
	score = 0
	sentiment = SentimentIntensityAnalyzer()
	for sentence in wiki.sentences:	
		polarity = sentence.sentiment.polarity
		subjectivity = sentence.sentiment.subjectivity
		numberOfSentences += 1
		score += polarity * subjectivity
		
	normalized_score = round(score/numberOfSentences,3)
	return normalized_score

def sentiment_label(score: int) -> str:
	#Classifying sentence based on score.
	if score > 0:
		sentiment_label = "positive"
	elif score < 0:
		sentiment_label = "negative"
	else:
		sentiment_label = "neutral"
	return sentiment_label

def preprocess_df(df: pd.DataFrame()) -> pd.DataFrame():
	# Remove the first row of dataframe
	df = df.iloc[1:]
	# Remove duplicated rows with the same link
	df.drop_duplicates(subset="link",keep=False, inplace=True)
	# Convert time in datetime 
	df['date'] = df['date'].apply(lambda text: convert_datetime(text))
	df['header'] = df['header'].apply(lambda text: preprocess(text))
	df['score'] = df['header'].apply(lambda text: sentiment_score(text))
	df['label'] = df['score'].apply(lambda text: sentiment_label(text))

	return df


abc_df = merge_csv_files('../raw_data/abc_10_Apr_2020')
abc_df = preprocess_df(abc_df)
print(abc_df.head(10))
print(abc_df.shape)
abc_df.to_csv('../processed_data/abc_10_Apr_2020.csv')
# print(sentiment_score("Pearls out, protests in: This generation of grandmothers is kicking the tired cliches aside"))
