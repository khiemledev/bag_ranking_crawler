import json
import re

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "luxcellent_content"
    queue_name = 'bag_ranking_crawl_link_luxcellent'

    # custom_settings = {
    #     "ITEM_PIPELINES": {
    #         "bag_ranking_crawler.pipelines.BagPipeline": 300,
    #     },
    # }

    def start_requests(self):
        credentials = pika.PlainCredentials(
            'admin',
            'emberyembery',
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                # host='rabbitmq.embery.com.au',
                # credentials=credentials,
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
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'method_frame': method_frame},
            )

    def parse(self, response):
        item = BagRankingCrawlerItem()
        item['website_name'] = 'luxcellent'

        item['link'] = response.url

        brand = response.css('.product__text.subtitle::text').get()
        item['brand'] = brand.strip() if brand is not None else None

        title = response.css('h1.product__title::text').get()
        item['title'] = title.strip() if title is not None else None

        price = response.css('.price-item::text').get()
        item['price'] = price.strip() if price is not None else None

        images = response.css('.thumbnail-list__item img::attr(srcset)').getall()
        for i in range(len(images)):
            img = images[i]
            img = img.split(',')[0].split(' ')[0]
            queries = img.split('?')[1].split('&')
            width = [query for query in queries if 'width=' in query][0]
            img = img.replace(width, 'width=1024')
            img = 'https:' + img
            images[i] = img

        item['images'] = ['https:' + img for img in images]

        if len(images) > 0:
            item['thumbnail'] = images[0]

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
