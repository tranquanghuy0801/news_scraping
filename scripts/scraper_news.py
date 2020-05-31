import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from newspaper import Article

# initialize datetime
date = datetime.now().strftime("%d_%b_%Y")

# Scrape News From Sydney Morning Herald


def scrape_smh(link: str, web_component: str, save_dir: str) -> None:
    # initialize dataframe
    dict_pd = {'link': [], 'header': [],
               'article': [], 'author': [], 'date': []}

    # request and get content from the link
    page = requests.get(link)
    soup = bs(page.content, 'html.parser')
    news = soup.find_all(web_component)

    # if news not None, proceed
    if news:
        for new in news:
            link_new = new['href']
            print(link_new)
            if link_new.endswith('html'):
                article = requests.get("https://www.smh.com.au" + link_new)
                soup = bs(article.content, 'html.parser')
                dict_pd['link'].append(link_new)
                if soup.find('h1'):
                    dict_pd['header'].append(soup.find('h1').text)
                else:
                    dict_pd['header'].append("")
                paragraphs = ' '.join(para.text for para in soup.find_all('p'))
                dict_pd['article'].append(paragraphs)
                if soup.find('aside'):
                    aside = soup.find('aside').text
                    date = re.findall(
                        r'(?:January|February|March|April|May|June|July|August|September\
                        |October|November|December)\s(?:\d|\d{2}),\s\d{4}', aside)
                    if len(date) > 0:
                        dict_pd['date'].append(date[0])
                        author = aside.split(date[0])[0].replace(
                            "Updated", "").replace("By", "").replace("and", ",")
                        dict_pd['author'].append(author)
                    else:
                        dict_pd['date'].append("")
                        dict_pd['author'].append("")
                else:
                    dict_pd['date'].append("")
                    dict_pd['author'].append("")

    # save to dataframe
    df = pd.DataFrame(dict_pd)
    df.to_csv(save_dir)
    print(df.head())

# Scrape News From ABC


def scrape_abc(link: str, save_dir: str) -> None:
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
            if len(link_new.split('/')) == 5 and link_new.startswith('/news/'):
                dict_pd['link'].append(link_new)
                article = requests.get("https://www.abc.net.au" + link_new)
                soup = bs(article.content, 'html.parser')
                article_section = soup.find("div", class_="article section")
                try:
                    dict_pd['header'].append(article_section.find('h1').text)
                except ValueError as ex:
                    dict_pd['header'].append("")
                    paragraphs = ' '.join(para.text for para in
                                article_section.find_all('p') if "\n" not in para)
                    dict_pd['article'].append(paragraphs)

                try:
                    author = article_section.find('div', class_="byline").text
                    author = author.replace("\n", "").strip()
                    dict_pd['author'].append(author)
                except ValueError as ex:
                    dict_pd['author'].append("")

                try:
                    date = article_section.find('span', class_="timestamp").text
                    date = re.findall(
                        r'(?:January|February|March|April|May|June|July|August|September\
                                        |October|November|December)\s(?:\d|\d{2}),\s\d{4}', date)
                    if len(date) > 0:
                        dict_pd['date'].append(date[0])
                    else:
                        dict_pd['date'].append("")
                except ValueError as ex:
                    dict_pd['date'].append("")


    except IndentationError as ex:
        print(ex)

    # Save dataframe to save directory
    df = pd.DataFrame(dict_pd)
    df.to_csv(save_dir)
    print(df.head())


# main run
if __name__ == "__main__":
    smh_headers = ['home', 'sydney', 'nsw', 'politics', 'business', 'world',
                'national', 'sport', 'culture', 'lifestyle', 'money',
                'education', 'healthcare', 'environment', 'technology']
    save_folder = "../raw_data/smh_" + date
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    for header in smh_headers:
        print("processing : " + header)
        save_dir = save_folder + "/smh_" + header.replace("home", "") + ".csv"
        scrape_smh("https://www.smh.com.au/" + header, "a", save_dir)

    # abc_headers = ['justin','politics','business','world','analysis-and-opinion',
                    #    'sport','science','health','arts-culture','factcheck','environment',
                    #    'technology','entertainment','music','rural']
    # save_folder = "../raw_data/abc_" + date
    # if not os.path.exists(save_folder):
    #     os.mkdir(save_folder)
    # for header in abc_headers:
    #     print("processing : " + header)
    #     save_dir = save_folder + "/abc_news_" + header.replace("-","_") + ".csv"
    #     scrape_abc("https://www.abc.net.au/news/" + header,save_dir)
