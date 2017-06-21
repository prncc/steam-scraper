# Steam Scraper

This repository contains [Scrapy](https://github.com/scrapy/scrapy) spiders for crawling products and scraping all user-submitted reviews from the [Steam game store](https://steampowered.com).
A few scripts for more easily managing and deploying the spiders are included as well.

## Installation

After cloning the repository with
```bash
git clone git@github.com:prncc/steam-scraper.git
```
start and activate a Python 3.6+ virtualenv with
```bash
cd steam-scraper
virtualenv -p python3.6 env
. env/bin/activate
```
Finally, install the used Python packages:
```bash
pip install -r requirements.txt
```
By the way, on macOS you can install Python 3.6 via [homebrew](https://brew.sh):
 ```bash
 brew install python3
```

On Ubuntu you can use [instructions posted on askubuntu.com](https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get).

## Crawling the Products

The purpose of `ProductSpider` is to discover product pages on the [Steam product listing](http://store.steampowered.com/search/?sort_by=Released_DESC) and extract useful metadata from them.
A neat feature of this spider is that it automatically handle's Steam's age verification gateways.
You can initiate the multi-hour crawl with
```bash
scrapy crawl products -o output/products_all.jl --logfile=output/products_all.log --loglevel=INFO -s JOBDIR=output/products_all_job -s HTTPCACHE_ENABLED=False
```
When it completes you should have metadata for all games on Steam in `output/products_all.jl`.
Here's some example output:
```python
{
  'app_name': 'Cold Fear™',
  'developer': 'Darkworks',
  'early_access': False,
  'genres': ['Action'],
  'id': '15270',
  'metascore': 66,
  'n_reviews': 172,
  'price': 9.99,
  'publisher': 'Ubisoft',
  'release_date': '2005-03-28',
  'reviews_url': 'http://steamcommunity.com/app/15270/reviews/?browsefilter=mostrecent&p=1',
  'sentiment': 'Very Positive',
  'specs': ['Single-player'],
  'tags': ['Horror', 'Action', 'Survival Horror', 'Zombies', 'Third Person', 'Third-Person Shooter'],
  'title': 'Cold Fear™',
  'url': 'http://store.steampowered.com/app/15270/Cold_Fear/'
 }
```

## Extracting the Reviews

The purpose of `ReviewSpider` is to scrape all user-submitted reviews of a particular product from the Steam community portal. 
By default, it starts from URLs listed in its `test_urls` parameter:
```python
class ReviewSpider(scrapy.Spider):
    name = 'reviews'
    test_urls = [
        "http://steamcommunity.com/app/316790/reviews/?browsefilter=mostrecent&p=1",  # Grim Fandango
        "http://steamcommunity.com/app/207610/reviews/?browsefilter=mostrecent&p=1",  # The Walking Dead
        "http://steamcommunity.com/app/414700/reviews/?browsefilter=mostrecent&p=1"   # Outlast 2
    ]
```
but can alternatively ingest a text file with contents of the form
```
http://steamcommunity.com/app/316790/reviews/?browsefilter=mostrecent&p=1
http://steamcommunity.com/app/207610/reviews/?browsefilter=mostrecent&p=1
http://steamcommunity.com/app/414700/reviews/?browsefilter=mostrecent&p=1
```
via the `url-file` command line argument:
```bash
scrapy crawl reviews -o reviews.jl -a url_file=url_file.txt -s JOBDIR=output/reviews
```
An output sample:
```python
{
  'date': '2017-06-04',
  'early_access': False,
  'found_funny': 5,
  'found_helpful': 0,
  'found_unhelpful': 1,
  'hours': 9.8,
  'page': 3,
  'page_order': 7,
  'product_id': '414700',
  'products': 179,
  'recommended': True,
  'text': '3 spooky 5 me',
  'user_id': '76561198116659822',
  'username': 'Fowler'
}
```

If you want to get all the reviews for all products, `split_review_urls.py` will remove duplicate entries from `products_all.jl` and shuffle `review_url`s into several text files.
This provides a convenient way to split up your crawl into manageable pieces.
The whole job takes a few days with Steam's generous rate limits.