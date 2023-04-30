import re
from datetime import datetime

import pymongo
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


def _strip(v):
    if v is None:
        return
    v = v.strip()
    if v == '':
        return
    return v

class ProductSpider(scrapy.Spider):
    name = "bot3"

    def start_requests(self):
        self.client = pymongo.MongoClient(
            "mongodb://admin:Embery#1234@51.161.130.170:27017")
        database_name = 'kl_bag_ranking'
        self.db = self.client[database_name]
        self.collection = self.db['bag_raw']
        self.collection.create_index('link', unique=True)

        items = self.collection.find(
            {
                "$or": [
                    {"is_sold": {"$exists": False}},
                    {"is_sold": {"$in": [False, None, ""]}}
                ],
            },
            {
                '_id': 1,
                'link': 1,
                'website_name': 1,
                'price': 1,
                'is_sold': 1,
                'sold_date': 1,
            })

        for item in items:
            self.logger.info(f'Check link {item["link"]}')
            item['_id'] = str(item['_id'])
            yield scrapy.Request(
                url=item['link'],
                callback=self.parse,
                meta={'item': item},
            )

    def parse(self, response):
        item = response.meta['item']
        website = item['website_name']

        status = response.status
        is_sold = None
        sold_price = None
        sold_date = None
        if status == 404:
            is_sold = True
            sold_date = datetime.now()

        elif website == 'bjluxury':
            price = response.css(
                '.woocommerce-Price-amount.amount').xpath('.//text()').get()
            price = _strip(price)
            if price is None:
                is_sold = True
                sold_date = datetime.now()

        elif website == 'emier':
            add_to_cart_ok = response.css('button[data-action="add-to-cart"]').get()
            is_sold = True if add_to_cart_ok is None else False
            if is_sold:
                sold_date = datetime.now()

        elif website == 'farfetch':
            # TODO: check later
            self.logger.info("Not enough information to check sold status")

        elif website == 'ginzaxiaoma':
            # TODO: check later
            self.logger.info("Not enough information to check sold status")

        elif website == 'handbagclinic':
            # TODO: check later
            self.logger.info("Not enough information to check sold status")

        elif website == 'janefinds':
            add_to_cart_text = response.css(
                '.add-to-cart__text::text').getall()
            if len(add_to_cart_text):
                add_to_cart_text = add_to_cart_text[0].strip().lower()
                if add_to_cart_text == 'sold out':
                    is_sold = True
                    sold_date = datetime.now()

        elif website == 'luxcellent':
            # TODO: check later
            self.logger.info("Not enough information to check sold status")

        elif website == 'madisonavenuecouture':
            # TODO: check later
            self.logger.info("Not enough information to check sold status")

        elif website == 'michaelsconsignment':
            price = response.css('.price-area .current-price::text').get()
            price = price.strip() if price is not None else None
            if price and price.lower() == 'sold out':
                is_sold = True
                sold_date = datetime.now()

        elif website == 'ounass':
            # TODO: check later
            self.logger.info("Not enough information to check sold status")

        elif website == 'thevintagebar':
            # TODO: check later
            self.logger.info("Not enough information to check sold status")

        elif website == 'vestiairecollective':
            price = response.css(
                'span[class^="product-price_productPrice__price"]::text').get()
            if price is None:
                price = response.css(
                    'div[class="product-price_productPrice__YKAe0"]').xpath(".//text()").extract()
                price = ''.join(price).strip()

                sold_re = re.compile(r'Sold at\s*\$(.+)\son\s*(.+)')
                sold = sold_re.search(price)
                if sold is not None:
                    is_sold = True
                    sold_price = sold.group(1)
                    sold_date = sold.group(2)

        elif website == 'worldsbest':
            # TOOD: check later
            self.logger.info("Not enough information to check sold status")

        updates = {}
        if is_sold is not None:
            updates['is_sold'] = is_sold
        if sold_price is not None:
            updates['sold_price'] = sold_price
        if sold_date is not None:
            updates['sold_date'] = sold_date

        if len(list(updates.keys())):
            self.logger.info(f'Update link {item["link"]} with {updates}')
            self.collection.update_one(
                {'_id': item['_id']},
                {'$set': updates},
            )
        else:
            self.logger.info(f'No update for link {item["link"]}')

        yield item
