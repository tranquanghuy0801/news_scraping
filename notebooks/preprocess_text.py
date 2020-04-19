import re
import nltk
import os
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from dateutil.parser import parse

def convert_datetime(text):
	"""Replace date format June 06, 2020 to 2020-06-06"""
	return str(parse(text).date())

def preprocess_text(sample):
	# 1. Remove non-letters        
    letters_only = re.sub("[^a-zA-Z]", " ", sample) 
    #
    # 2. Convert to lower case, split into individual words
    words = letters_only.lower().split()                             
    #
    # 3. In Python, searching a set is much faster than searching
    #   a list, so convert the stop words to a set
    stops = set(stopwords.words("english"))                  
    # 
    # 4. Remove stop words
    meaningful_words = [w for w in words if not w in stops]   
    #
    # 5. Join the words back into one string separated by space, 
    # and return the result.
    return( " ".join( meaningful_words ))