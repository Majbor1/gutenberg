import re
from collections import Counter
from scrapy.exceptions import DropItem


class ValidationPipeline:
    def process_item(self, item, spider):
        required_fields = ['title', 'upc', 'url']
        for field in required_fields:
            if not item.get(field):
                raise DropItem(f"Brak wymaganego pola '{field}' w: {item.get('url')}")

        if item.get('price') is None or item.get('price') < 0:
            raise DropItem(f"Nieprawidłowa cena w: {item.get('title')}")

        return item


class DuplicatePipeline:
    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        book_id = item.get('upc')
        if book_id in self.seen_ids:
            raise DropItem(f"Duplikat książki ID {book_id}: {item.get('title')}")
        self.seen_ids.add(book_id)
        return item


class TransformationPipeline:
    def process_item(self, item, spider):
        if 'category' in item:
            item['category'] = item['category'].lower()
        else:
            item['category'] = 'uncategorized'

        text = item.get('full_text', '')

        words = re.findall(r'[a-zA-Z]+', text.lower())
        letters = re.findall(r'[a-zA-Z]', text)

        item['num_words'] = len(words)
        item['num_letters'] = len(letters)
        item['most_common_words'] = Counter(words).most_common(10)

        item.pop('full_text', None)
        return item