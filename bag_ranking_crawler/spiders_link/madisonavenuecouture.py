# https://madisonavenuecouture.com/collections/hermes-handbags?page=4

import re

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "madisonavenuecouture_link"
    start_urls = [
        "https://madisonavenuecouture.com/collections/hermes-handbags?page={}".format(i) for i in range(1, 33)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        links = response.css('.inner.product-item a.product-grid-image::attr(href)').getall()
        for link in links:
            item = BagCrawlLink()
            item['website_name'] = 'madisonavenuecouture'
            item['link'] = 'https://madisonavenuecouture.com' + link
            self.logger.info('Found link: %s', item['link'])
            yield item
