import json

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "ounass_link"
    start_urls = [
        f"https://www.ounass.ae/api/v2/women/pre-loved/bags?fh_start_index={46 * (page - 1)}" for page in range(1, 3)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        data = json.loads(response.body)
        data = data['plp']['styleColors']
        for product in data:
            link = 'https://www.ounass.ae/' + product['slug'] + '.html'
            item = BagCrawlLink()
            item['link'] = link
            item['website_name'] = 'ounass'
            yield item
