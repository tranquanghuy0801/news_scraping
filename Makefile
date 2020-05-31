.PHONY = help run-web run-env run-scraper pylint test lock-req clean

PYTHON=$(which python3 | grep "python3")

.DEFAULT: help

help:
	@echo "make help - (all guide instructions for Makefile)"
	@echo "make run-env - (run virtual envrionment)"
	@echo "make run-web - (run the web app)"
	@echo "make run-scraper - (run the news scraper)"
	@echo "make pylint - (run the style guide pylint)"
	@echo "make test - (run test using pytest)"
	@echo "make lock-req - (run the locked dependecies of pipenv)"
	@echo "make clean - (clean unnecessary file)"

run-env:
	pipenv shell

run-web:
	PYTHON app.py

run-scraper:
	PYTHON scripts/scraper_news.py

pylint:
	pylint --rcfile=pylintrc -rn app scripts

test:
	pytest

lock-req:
	sh -c 'pipenv lock -r > requirements.txt'

clean:
	rm -rf .tox .DS_Store .pytest_cache .tmontmp .coverage .testmondata htmlcov build dist *.egg-info
