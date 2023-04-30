from operator import is_

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "loveluxury_link"
    start_urls = [
        *["https://loveluxury.co.uk/shop/hermes/page/{}".format(i) for i in range(1, 14)],
        *["https://loveluxury.co.uk/shop/chanel/page/{}".format(i) for i in range(1, 9)],
        *["https://loveluxury.co.uk/shop/louis-vuitton/page/{}".format(i) for i in range(1, 5)],
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        products = response.css(".product-col")
        for product in products:
            link = product.css('.product-loop-title').xpath('@href').get()
            item = BagCrawlLink()
            item['website_name'] = 'loveluxury'
            item['link'] = link
            yield item
