import json
from re import T

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


def get_body(page=1, item_per_page=20):
    t = str(item_per_page * page)
    body = {
        'action': 'load_more_product',
        'item_counter': t,
        'sold_item': "0",
        'grid': "5",
        'show_more': "false",
        'page': t,
        'brand[]': 'hermes',
        'price_order': "3",
    }
    return body

class ProductSpider(scrapy.Spider):
    name = "saclab_link"

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def start_requests(self):
        for i in range(5):
            yield scrapy.FormRequest(
                url='https://www.saclab.com/wp-admin/admin-ajax.php',
                formdata=get_body(page=i),
                callback=self.parse,
                method='POST',
            )

    def parse(self, response):
        products = response.css('.result__item')
        for product in products:
            link = product.css(
                'a.product-card__link::attr(href)').get()
            item = BagCrawlLink()
            item['link'] = link
            item['website_name'] = 'saclab'
            yield item
