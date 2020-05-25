import pytest
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scripts.preprocess_text import *
from scripts.export_data import convert_datetime,sentiment_score

def test_remove_url():
	assert remove_URL("") == ""
	assert remove_URL("https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below") == ""

def test_remove_non_ascii():
	assert remove_non_ascii([]) == []
	assert remove_non_ascii(["Huyền","Tú","Hoàng"]) == ["Huyen","Tu","Hoang"]

def test_replace_numbers():
	assert replace_numbers([]) == []
	assert replace_numbers(["sport","10","1234"]) == ["sport","ten","one thousand, two hundred and thirty-four"]

def test_replace_contractions():
	assert replace_contractions("you're they've") == "you are they have"

def test_convert_datetime():
	assert convert_datetime("June 06, 2020") == "2020-06-06"

def test_sentiment_score():
	assert type(sentiment_score("She is a beautiful girl in my class")) == type(0.55)
	assert type(sentiment_score("")) == type(0)
