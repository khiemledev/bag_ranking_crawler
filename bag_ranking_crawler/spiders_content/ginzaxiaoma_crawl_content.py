import json

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "ginzaxiaoma_content"
    queue_name = 'bag_ranking_crawl_link_ginzaxiaoma'

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.BagPipeline": 300,
        },
    }

    def start_requests(self):
        credentials = pika.PlainCredentials(
            'admin',
            'emberyembery',
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='rabbitmq.embery.com.au',
                credentials=credentials,
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=self.queue_name,
        )

        while True:
            method_frame, header_frame, body = self.channel.basic_get(
                queue=self.queue_name,
            )
            if method_frame is None:
                break

            url = json.loads(body.decode('utf-8').strip())['link']

            if not url:
                break

            self.logger.info("Crawling URL get from RabbitMQ: %s", url)
            yield scrapy.Request(url=url, callback=self.parse, meta={'method_frame': method_frame})

    def parse(self, response):
        item = BagRankingCrawlerItem()
        item['website_name'] = 'ginzaxiaoma'
        item['link'] = response.url

        data = json.loads(response.body)
        data = data['data']
        images = data['albumPics'].split(',')
        item['title'] = data['detailTitle']
        item['thumbnail'] = data['pic']
        item['images'] = images
        item['price'] = str(data['price']) + ' ' + data['currency']
        item['brand'] = data['brandName']
        item['model'] = data['attrModel']
        item['color'] = data['attrColors']
        item['material'] = data['attrMaterial']
        item['hardware'] = data['attrHardware']
        item['measurements'] = data['attrSize']
        item['condition'] = data['rank']

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
