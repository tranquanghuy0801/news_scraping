import re
import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

MONGO_URL = os.environ.get('MONGO_URL')

# initialize datetime
date = datetime.now().strftime("%d_%b_%Y")

# Scrape News From Sydney Morning Herald

def scrape_smh(collection, link: str, web_component: str) -> None:

    # request and get content from the link
    page = requests.get(link)
    soup = bs(page.content, 'html.parser')
    news = soup.find_all(web_component)

    # if news not None, proceed
    if news:
        for new in news:
            link_new = new['href']
            print(link_new)
            time.sleep(0.2)
            if link_new.endswith('html'):
                dict_pd = {}
                article = requests.get("https://www.smh.com.au" + link_new)
                soup = bs(article.content, 'html.parser')
                dict_pd['link'] = link_new
                if soup.find('h1'):
                    dict_pd['header'] = soup.find('h1').text
                else:
                    dict_pd['header'] = ""
                paragraphs = ' '.join(para.text for para in soup.find_all('p'))
                dict_pd['article'] = paragraphs
                if soup.find('aside'):
                    aside = soup.find('aside').text
                    date = re.findall(
                        r'(?:January|February|March|April|May|June|July|August|September\
                        |October|November|December)\s(?:\d|\d{2}),\s\d{4}', aside)
                    if len(date) > 0:
                        dict_pd['date'] = date[0]
                        author = aside.split(date[0])[0].replace(
                            "Updated", "").replace("By", "").replace("and", ",")
                        dict_pd['author'] = author
                    else:
                        dict_pd['date'] = ""
                        dict_pd['author'] = ""
                else:
                    dict_pd['date'] = ""
                    dict_pd['author'] = ""
                dict_pd['source'] = "smh"
                try:
                    x = collection.insert_one(dict_pd)
                    print(x.inserted_id)
                except Exception as ex:
                    print("cannot insert data")

# Scrape News From ABC

def scrape_abc(collection, link: str) -> None:
    # initialize dataframe
    dict_pd = {'link': [], 'header': [],
               'article': [], 'author': [], 'date': []}

    # request and get content from the link
    page = requests.get(link)
    soup = bs(page.content, 'html.parser')
    if soup.find("div", class_="page section"):
        news = soup.find("div", class_="page section").find_all("a")
    elif soup.find("main", id="content"):
        news = soup.find("main", id="content").find_all("a")
    else:
        news = soup.find("div", id="main-content").find_all("a")

    try:
        for new in news:
            link_new = new['href']
            print(link_new)
            time.sleep(0.3)
            if len(link_new.split('/')) == 5 and link_new.startswith('/news/'):
                article = requests.get("https://www.abc.net.au" + link_new)
                soup = bs(article.content, 'html.parser')
                article_section = soup.find("div", class_="article section")
                if article_section:
                    dict_pd = {}
                    dict_pd['link'] = link_new
                    try:
                        dict_pd['header'] = article_section.find('h1').text
                    except Exception as ex:
                        dict_pd['header'] = ""
                    try:
                        paragraphs = ' '.join(para.text for para in
                                    article_section.find_all('p') if "\n" not in para)
                        dict_pd['article'] = paragraphs
                    except Exception as ex:
                        dict_pd['article'] = ""
                    try:
                        author = article_section.find('div', class_="byline").text
                        author = author.replace("\n", "").strip()
                        dict_pd['author'] = author
                    except Exception as ex:
                        dict_pd['author'] = ""

                    try:
                        date = article_section.find('span', class_="timestamp").text
                        date = re.findall(
                            r'(?:January|February|March|April|May|June|July|August|September\
                                            |October|November|December)\s(?:\d|\d{2}),\s\d{4}', date)
                        if len(date) > 0:
                            dict_pd['date'] = date[0]
                        else:
                            dict_pd['date'] = ""
                    except Exception as ex:
                        dict_pd['date'] = ""
                    dict_pd['source'] = "abc"
                    try:
                        x = collection.insert_one(dict_pd)
                        print(x.inserted_id)
                    except Exception as ex:
                        print("cannot insert data")
    except Exception as ex:
        print(ex)

# main run
if __name__ == "__main__":
    try:
        client = MongoClient(MONGO_URL)
        collection = client.db.raw
        smh_headers = ['home', 'sydney', 'nsw', 'politics', 'business', 'world',
                    'national', 'sport', 'culture', 'lifestyle', 'money',
                    'education', 'healthcare', 'environment', 'technology']
        for header in smh_headers:
            print("processing : SMH - " + header)
            scrape_smh(collection, "https://www.smh.com.au/" + header, "a")

        abc_headers = ['justin', 'politics', 'business', 'world', 'analysis-and-opinion',
                        'sport', 'science', 'health', 'arts-culture', 'factcheck', 'environment',
                        'technology', 'entertainment', 'music', 'rural']
        for header in abc_headers:
            print("processing : ABC - " + header)
            scrape_abc(collection, "https://www.abc.net.au/news/" + header)
    except Exception as ex:
        print("Cannot crawl the data")
