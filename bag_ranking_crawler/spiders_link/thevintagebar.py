import re

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "thevintagebar_link"
    start_urls = [
        "https://thevintagebar.com/bags/hermes-bags?page={}".format(i) for i in range(1, 26)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        products = response.css(
            ".products-cards .card-box")
        for product in products:
            link = product.css(
                ".item-image a.img-link::attr(href)").extract_first()
            item = BagCrawlLink()
            item['website_name'] = "thevintagebar"
            item['link'] = "https://thevintagebar.com" + link
            self.logger.info(link)
            yield item
