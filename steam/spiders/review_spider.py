import re

import scrapy
from scrapy.http import FormRequest, Request
from w3lib.url import url_query_parameter

from ..items import ReviewItem, ReviewItemLoader, str_to_int


def load_review(review, product_id, page, order):
    """
    Load a ReviewItem from a single review.
    """
    loader = ReviewItemLoader(ReviewItem(), review)

    loader.add_value('product_id', product_id)
    loader.add_value('page', page)
    loader.add_value('page_order', order)

    # Review data.
    loader.add_css('recommended', '.title::text')
    loader.add_css('date', '.date_posted::text', re='Posted: (.+)')
    loader.add_css('text', '.apphub_CardTextContent::text')
    loader.add_css('hours', '.hours::text', re='(.+) hrs')
    loader.add_css('compensation', '.received_compensation::text')

    # User/reviewer data.
    loader.add_css('user_id', '.apphub_CardContentAuthorName a::attr(href)', re='.*/profiles/(.+)/')
    loader.add_css('username', '.apphub_CardContentAuthorName a::text')
    loader.add_css('products', '.apphub_CardContentMoreLink ::text', re='([\d,]+) product')

    # Review feedback data.
    feedback = loader.get_css('.found_helpful ::text')
    loader.add_value('found_helpful', feedback, re='([\d,]+) of')
    loader.add_value('found_unhelpful', feedback, re='of ([\d,]+)')
    loader.add_value('found_funny', feedback, re='([\d,]+).*funny')

    early_access = loader.get_css('.early_access_review')
    if early_access:
        loader.add_value('early_access', True)
    else:
        loader.add_value('early_access', False)

    return loader.load_item()


def get_page(response):
    from_page = response.meta.get('from_page', None)

    if from_page:
        page = from_page + 1
    else:
        page = url_query_parameter(response.url, 'p', None)
        if page:
            page = str_to_int(page)

    return page


def get_product_id(response):
    product_id = response.meta.get('product_id', None)

    if not product_id:
        try:
            return re.findall("app/(.+?)/", response.url)[0]
        except:  # noqa E722
            return None
    else:
        return product_id


class ReviewSpider(scrapy.Spider):
    name = 'reviews'
    test_urls = [
        # Full Metal Furies
        'http://steamcommunity.com/app/416600/reviews/?browsefilter=mostrecent&p=1',
    ]

    def __init__(self, url_file=None, steam_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_file = url_file
        self.steam_id = steam_id

    def read_urls(self):
        with open(self.url_file, 'r') as f:
            for url in f:
                url = url.strip()
                if url:
                    yield scrapy.Request(url, callback=self.parse)

    def start_requests(self):
        if self.steam_id:
            url = (
                f'http://steamcommunity.com/app/{self.steam_id}/reviews/'
                '?browsefilter=mostrecent&p=1'
            )
            yield Request(url, callback=self.parse)
        elif self.url_file:
            yield from self.read_urls()
        else:
            for url in self.test_urls:
                yield Request(url, callback=self.parse)

    def parse(self, response):
        page = get_page(response)
        product_id = get_product_id(response)

        # Load all reviews on current page.
        reviews = response.css('div .apphub_Card')
        for i, review in enumerate(reviews):
            yield load_review(review, product_id, page, i)

        # Navigate to next page.
        form = response.xpath('//form[contains(@id, "MoreContentForm")]')
        if form:
            yield self.process_pagination_form(form, page, product_id)

    def process_pagination_form(self, form, page=None, product_id=None):
        action = form.xpath('@action').extract_first()
        names = form.xpath('input/@name').extract()
        values = form.xpath('input/@value').extract()

        formdata = dict(zip(names, values))
        meta = dict(prev_page=page, product_id=product_id)

        return FormRequest(
            url=action,
            method='GET',
            formdata=formdata,
            callback=self.parse,
            meta=meta
        )
