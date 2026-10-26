import re
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def clean_text(text):
    return text.strip()


def downloads_to_rating(downloads_text):
    match = re.search(r'\d+', downloads_text)
    downloads = int(match.group()) if match else 0
    if downloads >= 1000:
        return 5
    elif downloads >= 500:
        return 4
    elif downloads >= 100:
        return 3
    elif downloads >= 20:
        return 2
    return 1


def parse_price(val):
    return float(val)

class BookItem(scrapy.Item):
    title = scrapy.Field()
    category = scrapy.Field()
    rating = scrapy.Field()
    availability = scrapy.Field()
    upc = scrapy.Field()               
    url = scrapy.Field()
    price = scrapy.Field()            
    full_text = scrapy.Field()         
    num_words = scrapy.Field()
    num_letters = scrapy.Field()
    most_common_words = scrapy.Field()


class GutenbergBookLoader(ItemLoader):
    default_item_class = BookItem
    default_output_processor = TakeFirst()

    title_in = MapCompose(clean_text)
    category_in = MapCompose(clean_text)
    rating_in = MapCompose( clean_text, downloads_to_rating)
    availability_in = MapCompose(clean_text)
    upc_in = MapCompose(clean_text)
    price_in = MapCompose(parse_price)