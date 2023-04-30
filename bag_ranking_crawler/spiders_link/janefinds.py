import re

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "janefinds_link"
    start_urls = [
        "https://janefinds.com/collections/hermes?page={}".format(i) for i in range(1, 35)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = response.css(".product-item")
        for product in products:
            link = 'https://janefinds.com' + \
                product.css("a").xpath("@href").get()

            item = BagCrawlLink()
            item['website_name'] = 'janefinds'
            item['link'] = link
            yield item
