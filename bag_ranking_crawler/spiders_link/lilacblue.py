from operator import is_

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "lilacblue_link"
    start_urls = [
        *[f"https://lilacblue.com/product-category/hermes-birkin-kelly-bags/calf-leather-exotic-birkins/page/{i}" for i in range(1, 43)],
        *[f"https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-kelly-bags/page/{i}" for i in range(1, 34)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-bolide-evelyne-new/page/{i}' for i in range(1, 3)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-constance-and-others/page/{i}' for i in range(1, 11)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-picotin-new/page/{i}' for i in range(1, 4)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-lindy-new/page/{i}' for i in range(1, 2)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-herbag-new/page/{i}' for i in range(1, 2)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-jige-garden-party-more/page/{i}' for i in range(1, 3)],
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        products = response.css(".product")
        for product in products:
            link = product.css('.product-title a').xpath('@href').get()
            if link is None:
                continue
            item = BagCrawlLink()
            item['link'] = link
            item['website_name'] = 'lilacblue'
            # self.logger.info(link)
            yield item
