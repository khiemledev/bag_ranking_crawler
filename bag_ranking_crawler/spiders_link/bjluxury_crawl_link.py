from operator import is_

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "bjluxury_link"
    start_urls = [
        *["https://bjluxury.com/all-hermes-bags/?product-page={}&count=36".format(
            i) for i in range(1, 78)],
        *["https://bjluxury.com/all-chanel-bags/?product-page={}&count=36".format(i) for i in range(1, 25)]
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingPipeline": 300,
        },
    }

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = response.css(".product")
        for product in products:
            link = product.css("a").xpath("@href").get()
            item = BagCrawlLink()
            item['website_name'] = 'bjluxury'
            item['link'] = link
            yield item
