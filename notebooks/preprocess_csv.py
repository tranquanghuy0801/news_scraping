import pandas as pd
import os
import fnmatch
import glob
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from preprocess_text import *
from textblob import TextBlob
from datetime import datetime
from dateutil.parser import parse

# initialize datetime 
date = datetime.now().strftime("%d_%b_%Y")

def convert_datetime(text):
	"""Replace date format June 06, 2020 to 2020-06-06"""
	try:
		return str(parse(text).date())
	except:
		return ""

def merge_csv_files(directory: str,pattern = "*.csv") -> pd.DataFrame(): 

	# Initialize DataFrame
	df = pd.DataFrame()

	for folder in os.listdir(directory):
		if folder.endswith('2020'):
			# List all files in this directory 
			folder = os.path.join(directory,folder)
			for root, dirs, files in os.walk(folder):
				for basename in files:
					if fnmatch.fnmatch(basename, pattern):
						filename = os.path.join(root, basename)
						print(filename)
						csv_df = pd.read_csv(filename,header=None,names=['link','header','article','author','date'])
						csv_df['source'] = filename.replace('../raw_data/','')[:3]
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
		
	if numberOfSentences < 1:
		normalized_score = round(score,3)
	else:
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

def clean_df(df: pd.DataFrame()) -> pd.DataFrame():
	# Remove the first row of dataframe
	df = df.iloc[1:]
	df = df[df['header'] != '']
	# Remove duplicated rows with the same link
	df.drop_duplicates(subset="link",keep=False, inplace=True)
	# Convert time in datetime 
	df['date'] = df['date'].apply(lambda text: convert_datetime(text))
	df['header'] = df['header'].apply(lambda text: preprocess(text))
	df['article'] = df['article'].apply(lambda text: preprocess(text))
	df['score'] = df['header'].apply(lambda text: sentiment_score(text))
	df['label'] = df['score'].apply(lambda text: sentiment_label(text))

	return df

save_dir = "../processed_data/news_" + date + ".csv"
abc_df = merge_csv_files('../raw_data')
abc_df = clean_df(abc_df)
print(abc_df.head(10))
print(abc_df.shape)
abc_df.to_csv(save_dir)
# print(sentiment_score("Pearls out, protests in: This generation of grandmothers is kicking the tired cliches aside"))
