import json

import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "handbagclinic_content"
    start_urls = [f"https://www.handbagclinic.co.uk/hermes?page={i}&json=" for i in range(1, 3)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.BagPipeline": 300,
        },
    }

    def parse(self, response):
        data = json.loads(response.body)
        products = data['listings']['data']

        for product in products:
            item = BagRankingCrawlerItem()
            item['website_name'] = 'handbagclinic'

            item['link'] = 'https://www.handbagclinic.co.uk' + product['url']
            item['title'] = product['name']
            item['model'] = product['model']
            item['brand'] = product['manufacturer']
            item['images'] = ['https://f08c4e54.aerocdn.com/image-factory/768x768/' + e['file']
                              for e in product['images']]
            if len(item['images']) > 0:
                item['thumbnail'] = item['images'][0]

            item['description'] = product['summary']

            item['price'] = product['price']['value']['ex']

            item['is_sold'] = not product['buyable']

            self.logger.info(item)
            yield item
