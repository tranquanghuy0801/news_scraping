# Australian News Analytics Dashboard

![build](https://github.com/tranquanghuy0801/news_scraping/workflows/Python%20Web%20Analytics%20application/badge.svg)

This project intends to analyse reliable Australian source news and displays the statistics with dashboards. More detailed information will be updated soon.

## Last Update (25/05/2020)

Dashboard made with Dash & Plotly

![Draft Dashboard](images/dashboard.png)

## Update the project progress

- [ ] <b>Crawl the news</b>
  - [x] ABC News
  - [x] The Sydney Morning Herald
  - [ ] The Australian Financial Review
  - [ ] The Australian
  - [ ] The Canberra Times
  - [ ] Daily Telegraph
  - [ ] Northern Territory News
  - [ ] The Courier-Mail
  - [ ] The West Australian
- [ ] <b>Analyze the news</b>
  - [ ] preprocess the text
  - [x] sentiment analysis on header
  - [x] sentiment analysis on header + content  
  - [x] topic modelling using LDA
- [ ] <b>Make a dashboarb visualization</b>
  - [x] make a draft dashboard
  - [ ] change bar graph to word cloud
- [ ] <b>Deploy real-time website</b>
  - [x] deploy website
  - [x] set up CI/CD pipeline using Github Actions & Heroku
  - [ ] real-time update
- [ ] <b> Monitor website & upgrade plans</b>

## Instructions

#### Install the dependency

- Using pipenv

```
pip install pipenv
pipenv install --dev
```

- Using virtualenv

```
virtualenv -p python3 <name_env>
source <name_env>/bin/activate
pip install -r requirements.txt
```

### Create .env

- Create a file <b>.env</b> in the main directory and add the code below and replace the information

```
DATABASE_URL='*****'
TABLE_NAME='*****'
secret_key='*****'
```  

#### Run Commands

- See <b>Makefile</b> for more instructions

## Authors

- **Harry Tran**

## License

This project is licensed under the GNU License - see the [LICENSE.md](LICENSE.md) file for details
