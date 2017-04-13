import scrapy
from scrapy.http import FormRequest
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from ..items import ReviewItem


def load_review(review):
    """
    Load a ReviewItem from a single review.
    """
    loader = ItemLoader(
        ReviewItem(default_output_processor=TakeFirst()), review)

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

    return loader.load_item()


class ReviewSpider(scrapy.Spider):
    name = 'steam'
    start_urls = ["http://store.steampowered.com/search/"]

    def parse(self, response):
        # Load all reviews on current page.
        reviews = response.css('div .apphub_Card')
        for review in reviews:
            yield load_review(review)

        form = response.css('form')
        yield self.process_pagination_form(form)

    def process_pagination_form(self, form):
        action = form.xpath('@action').extract_first()
        names = form.xpath('input/@name').extract()
        values = form.xpath('input/@id').extract()

        formdata = dict(zip(names, values))

        return FormRequest(
            url=action,
            method='GET',
            formdata=formdata,
            callback=self.parse
        )

