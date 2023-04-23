import json

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "farfetch_link"
    start_urls = [
        *["https://www.farfetch.com/vn/plpslice/listing-api/products-facets?page={}&view=90&scale=274&pagetype=Shopping&rootCategory=Women&pricetype=FullPrice&c-designer=70015".format(
            i) for i in range(1, 14)],
        *["https://www.farfetch.com/vn/plpslice/listing-api/products-facets?page={}&view=90&scale=274&pagetype=Shopping&rootCategory=Men&pricetype=FullPrice&c-designer=70015".format(i) for i in range(1, 3)],]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = json.loads(response.body)['listingItems']['items']
        for product in products:
            link = 'https://www.farfetch.com'+product['url']
            item = BagCrawlLink()
            item['website_name'] = 'farfetch'
            item['link'] = link
            yield item
