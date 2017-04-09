# -*- coding: utf-8 -*-
from datetime import datetime, date

import scrapy
from scrapy.loader.processors import TakeFirst, Compose, Join, MapCompose


def simplify_recommended(x):
    return False if x == 'Not Recommended' else True


def strip_text(x):
    return x.strip(u'\n\t\r')


def str_to_float(x):
    x = x.replace(',', '')
    try:
        return float(x)
    except:
        x


def str_to_int(x):
    try:
        return int(str_to_float(x))
    except:
        return x

def standardize_date(x):
    """
    Convert x from recognized input formats to desired output format,
    or leave unchanged if input format is not recognized.
    """
    try:
        return datetime.strptime(x, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Induce year
    try:
        d = datetime.strptime(x, "%B %d")
        d = d.replace(year=date.today().year)
        return d.strftime("%Y-%m-%d")
    except ValueError:
        pass

    return x


class ProductItem(scrapy.Item):
    specs = scrapy.Field(
        output_processor=MapCompose(strip_text)
    )
    tags = scrapy.Field(
        output_processor=MapCompose(strip_text)
    )


class ReviewItem(scrapy.Item):
    recommended = scrapy.Field(
        input_processor=simplify_recommended,
        output_processor=TakeFirst(),
    )
    date = scrapy.Field(
        output_processor=Compose(TakeFirst(), standardize_date)
    )
    text = scrapy.Field(
        input_processor=MapCompose(strip_text),
        output_processor=Compose(Join('\n'), strip_text)
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
    compensation = scrapy.Field(
        output_processor=TakeFirst()
    )
    username = scrapy.Field(
        output_processor=TakeFirst()
    )
    user_id = scrapy.Field(
        output_processor=TakeFirst()
    )
    products = scrapy.Field(
        output_processor=Compose(TakeFirst(), str_to_int)
    )

