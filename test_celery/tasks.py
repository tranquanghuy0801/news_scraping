from __future__ import absolute_import
from test_celery.celery import app
import requests
import time
from newspaper import Article
#from pymongo import MongoClient
#client = MongoClient('10.1.1.234', 27018) # change the ip and port to your mongo database's
#db = client.mongodb_test
#collection = db.celery_test
#post = db.test
@app.task(bind=True,default_retry_delay=10) # set a retry delay, 10 equal to 10s
def scrape_news(self,link):
	try:
	    page = requests.get(link)
	    soup = bs(page.content, 'html.parser')
	    news = soup.find_all("a")
		

	except Exception as exc:
        raise self.retry(exc=exc)
