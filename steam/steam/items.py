from datetime import datetime, date
import logging

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Join, MapCompose, TakeFirst

logger = logging.getLogger(__name__)


class StripText:
    def __init__(self, chars=' \r\t\n'):
        self.chars = chars

    def __call__(self, value):
        try:
            return value.strip(self.chars)
        except:
            return value


def simplify_recommended(x):
    return False if x == 'Not Recommended' else True


def standardize_date(x):
    """
    Convert x from recognized input formats to desired output format,
    or leave unchanged if input format is not recognized.
    """
    try:
        return datetime.strptime(x, "%b %d, %Y").strftime("%Y-%m-%d")
    except ValueError as e:
        logger.debug(f"Failed to process '{x}': {e.args[0]}.")
        pass

    # Induce year to current year if it is missing.
    try:
        d = datetime.strptime(x, "%b %d")
        d = d.replace(year=date.today().year)
        return d.strftime("%Y-%m-%d")
    except ValueError as e:
        logger.debug(f"Failed to process '{x}': {e.args[0]}.")
        pass

    return x


def str_to_float(x):
    x = x.replace(',', '')
    try:
        return float(x)
    except:
        return x


def str_to_int(x):
    try:
        return int(str_to_float(x))
    except:
        return x


class ProductItem(scrapy.Item):
    url = scrapy.Field()
    id = scrapy.Field()
    app_name = scrapy.Field()
    reviews_url = scrapy.Field()
    title = scrapy.Field()
    genres = scrapy.Field(
        output_processor=Compose(TakeFirst(), lambda x: x.split(','), MapCompose(StripText()))
    )
    developer = scrapy.Field()
    publisher = scrapy.Field()
    release_date = scrapy.Field(
        output_processor=Compose(TakeFirst(), StripText(), standardize_date)
    )
    specs = scrapy.Field(
        output_processor=MapCompose(StripText())
    )
    tags = scrapy.Field(
        output_processor=MapCompose(StripText())
    )
    price = scrapy.Field(
        output_processor=Compose(TakeFirst(),
                                 StripText(chars=' $\n\t\r'),
                                 str_to_float)
    )
    discount_price = scrapy.Field(
        output_processor=Compose(TakeFirst(),
                                 StripText(chars=' $\n\t\r'),
                                 str_to_float)
    )
    sentiment = scrapy.Field()
    n_reviews = scrapy.Field(
        output_processor=Compose(
            MapCompose(StripText(), lambda x: x.replace(',', ''), str_to_int),
            max
        )
    )
    metascore = scrapy.Field(
        output_processor=Compose(TakeFirst(), StripText(), str_to_int)
    )
    early_access = scrapy.Field()


class ReviewItem(scrapy.Item):
    product_id = scrapy.Field()
    recommended = scrapy.Field(
        input_processor=simplify_recommended,
        output_processor=TakeFirst(),
    )
    date = scrapy.Field(
        output_processor=Compose(TakeFirst(), standardize_date)
    )
    text = scrapy.Field(
        input_processor=MapCompose(StripText()),
        output_processor=Compose(Join('\n'), StripText())
    )
    hours = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_float)
    )
    found_helpful = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    found_unhelpful = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    found_funny = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )
    compensation = scrapy.Field()
    username = scrapy.Field()
    user_id = scrapy.Field()
    products = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )


class ProductItemLoader(ItemLoader):
    default_output_processor=Compose(TakeFirst(), StripText())


class ReviewItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
