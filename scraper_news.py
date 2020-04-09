import requests 
from bs4 import BeautifulSoup as bs
import pandas as pd 
import re 

# Scrape News From Sydney Morning Herald
def scrape_smh(link: str,web_component: str,save_dir: str):
	# initialize dataframe 
	dict_pd = {'link': [],'header': [],'article':[],'author': [],'date':[]}

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
				article = requests.get("https://www.smh.com.au" + link_new )
				soup = bs(article.content, 'html.parser')
				dict_pd['link'].append(link_new )
				if soup.find('h1'):
					dict_pd['header'].append(soup.find('h1').text)
				else:
					dict_pd['header'].append("")
				paragraphs = ' '.join(para.text for para in soup.find_all('p'))
				dict_pd['article'].append(paragraphs)
				if soup.find('aside'):
					aside = soup.find('aside').text 
					date = re.findall(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s(?:\d|\d{2}),\s\d{4}',aside)
					if len(date) > 0:
						dict_pd['date'].append(date[0])
						author = aside.split(date[0])[0].replace("Updated","").replace("By","").replace("and",",")
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

def scrape_abc():
	return 

if __name__ == "__main__":
	headers = ['home','sydney','nsw','politics','business','world','national','property','sport','culture','lifestyle','money','education','healthcare','environment','technology']
	for header in headers:
		if header == "home":
			header = ""
		scrape_smh("https://www.smh.com.au/" + header,"a","data/sydney_herald_" + header + ".csv")
