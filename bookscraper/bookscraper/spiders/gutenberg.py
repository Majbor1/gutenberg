import re
import scrapy
from bookscraper.items import GutenbergBookLoader

class GutenbergSpider(scrapy.Spider):
    name = "gutenberg"
    allowed_domains = ["www.gutenberg.org"]
    start_urls = ["https://www.gutenberg.org/ebooks/79828"]

    def parse(self, response):
        loader = GutenbergBookLoader(response=response)

        loader.add_xpath("title", '//h1/text()')
        loader.add_xpath(
            "category",
            '//th[contains(text(), "Subject") or contains(text(), "Category") or contains(text(), "LoC Class")]/following-sibling::td//text()'
        )
        loader.add_xpath("rating", '//th[contains(text(), "Downloads")]/following-sibling::td/text()')
        loader.add_xpath("availability", '//th[contains(text(), "Copyright Status")]/following-sibling::td/text()')
        loader.add_xpath("upc", '//th[contains(text(), "EBook-No.")]/following-sibling::td/text()')
        
        book_id_match = re.search(r'/ebooks/(\d+)', response.url)
        if book_id_match:
            loader.add_value("upc", book_id_match.group(1))

        loader.add_value("url", response.url)
        loader.add_value("price", 0.0)

        item = loader.load_item()

        txt_link = response.xpath(
            '//a[contains(text(), "Plain Text") or contains(@type, "text/plain")]/@href'
        ).get()

        if txt_link:
            yield response.follow(
                txt_link,
                callback=self.parse_text,
                cb_kwargs={"item": item},
                dont_filter=True
            )
        else:
            item["full_text"] = " ".join(response.css("table.bibrec ::text").getall())
            yield item

        if book_id_match:
            current_id = int(book_id_match.group(1))
            next_id = current_id - 1
            if next_id > 0:
                next_book_url = f"https://www.gutenberg.org/ebooks/{next_id}"
                yield response.follow(next_book_url, callback=self.parse)

    def parse_text(self, response, item):
        item["full_text"] = response.text
        yield item
