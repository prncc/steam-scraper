import logging
import re
from w3lib.url import canonicalize_url, url_query_cleaner

from scrapy.http import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import ProductItem, ProductItemLoader

logger = logging.getLogger(__name__)


def load_product(response):
    """Load a ProductItem from the product page response."""
    loader = ProductItemLoader(item=ProductItem(), response=response)

    url = url_query_cleaner(response.url, ['snr'], remove=True)
    url = canonicalize_url(url)
    loader.add_value('url', url)

    found_id = re.findall('/app/(.*?)/', response.url)
    if found_id:
        id = found_id[0]
        reviews_url = f"http://steamcommunity.com/app/{id}/reviews/?browsefilter=mostrecent&p=1"
        loader.add_value('reviews_url', reviews_url)
        loader.add_value('id', id)

    # Publication details.
    details = response.css('.details_block').extract_first()
    try:
        details = details.split('<br>')

        for line in details:
            line = re.sub('<[^<]+?>', '', line)  # Remove tags.
            line = re.sub('[\r\t\n]', '', line).strip()
            for prop, name in [
                ('Title:', 'title'),
                ('Genre:', 'genres'),
                ('Developer:', 'developer'),
                ('Publisher:', 'publisher'),
                ('Release Date:', 'release_date')
            ]:
                if prop in line:
                    item = line.replace(prop, '').strip()
                    loader.add_value(name, item)
    except:
        pass

    loader.add_css('app_name', '.apphub_AppName ::text')
    loader.add_css('specs', '.game_area_details_specs a ::text')
    loader.add_css('tags', 'a.app_tag::text')

    price = response.css('.game_purchase_price ::text').extract_first()
    if not price:
        price = response.css('.discount_original_price ::text').extract_first()
        loader.add_css('discount_price', '.discount_final_price ::text')
    loader.add_value('price', price)

    sentiment = response.css('.game_review_summary').xpath(
        '../*[@itemprop="description"]/text()').extract()
    loader.add_value('sentiment', sentiment)
    loader.add_css('n_reviews', '.responsive_hidden', re='\(([\d,]+) reviews\)')

    loader.add_xpath(
        'metascore',
        '//div[@id="game_area_metascore"]/div[contains(@class, "score")]/text()')

    return loader.load_item()


class ProductsSpider(CrawlSpider):
    name = 'products'
    start_urls = [
        "http://store.steampowered.com/app/475320/"
    ]

    allowed_domains=["steampowered.com"]

    rules = [
        Rule(LinkExtractor(
                allow='/app/(.+)/',
                restrict_css='#search_result_container'),
             callback='parse_product'),
        Rule(LinkExtractor(
                allow='page=(\d+)',
                restrict_css='.search_pagination_right'))
    ]

    def parse_product(self, response):
        # Circumvent age selection form.
        if '/agecheck/app' in response.url:
            logger.debug(f"Form-type age check triggered for {response.url}.")

            form = response.css('#agegate_box form')

            action = form.xpath('@action').extract_first()
            name = form.xpath('input/@name').extract_first()
            value = form.xpath('input/@value').extract_first()

            formdata = {
                name: value,
                'ageDay': '1',
                'ageMonth': '1',
                'ageYear': '1955'
            }

            yield FormRequest(
                url=action,
                method='POST',
                formdata=formdata,
                callback=self.parse_product
            )

        else:
            yield load_product(response)
