from datetime import datetime, date

import scrapy
from scrapy.loader.processors import MapCompose, Compose, TakeFirst


def standardize_date(x):
    """
    Convert x from recognized input formats to desired output format,
    or leave unchanged if input format is not recognized.
    """
    try:
        return datetime.strptime(x, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Induce year.
    try:
        d = datetime.strptime(x, "%B %d")
        d = d.replace(year=date.today().year)
        return d.strftime("%Y-%m-%d")
    except ValueError:
        pass

    return x


def strip_text(x):
    return x.strip(u'\n\t\r')


class ProductItem(scrapy.Item):
    url = scrapy.Field(output_processor=TakeFirst())
    id = scrapy.Field(output_processor=TakeFirst())
    reviews_url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    genre = scrapy.Field()
    developer = scrapy.Field(output_processor=TakeFirst())
    publisher = scrapy.Field(output_processor=TakeFirst())
    release_date = scrapy.Field(
        output_processor=Compose(TakeFirst(), standardize_date)
    )
    specs = scrapy.Field(
        output_processor=MapCompose(strip_text)
    )
    tags = scrapy.Field(
        output_processor=MapCompose(strip_text)
    )