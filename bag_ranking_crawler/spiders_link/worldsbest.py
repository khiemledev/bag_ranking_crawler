import re

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "worldsbest_link"
    start_urls = [
        "https://www.worldsbest.com/fashion/handbags/hermes?page={}".format(i) for i in range(1, 5)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        products = response.css(
            ".node.node-product-display")
        for product in products:
            link = product.css("a::attr(href)").extract_first()
            item = BagCrawlLink()
            item['website_name'] = "worldsbest"
            item['link'] = "https://www.worldsbest.com" + link
            self.logger.info(link)
            yield item
