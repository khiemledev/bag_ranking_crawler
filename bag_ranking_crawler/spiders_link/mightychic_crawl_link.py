from operator import is_

import scrapy

from bag_ranking_crawler.items import BagCrawlLink

base_url = "https://mightychic.com/collections/all-hermes-bags?view=infinite-scroll"


class ProductSpider(scrapy.Spider):
    name = "mightychic_link"
    start_urls = [f"{base_url}&page=1"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        products = response.css(".collection__item")
        for product in products:
            link = 'https://mightychic.com' + \
                product.css("h2").xpath(".//a/@href").get()
            item = BagCrawlLink()
            item['link'] = link
            item['website_name'] = 'mightychic'
            yield item
