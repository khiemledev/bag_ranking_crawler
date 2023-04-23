import json

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "bjluxury_content"
    queue_name = 'bag_ranking_crawl_link_bjluxury'

    def start_requests(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
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

        title = response.css('.product_title').xpath('.//text()').get()
        item['title'] = title

        shop_attributes = response.css('.shop_attributes')
        item['brand'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--brand > td'
        ).xpath('.//text()').get()
        item['model'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--attribute_pa_model > td'
        ).xpath('.//text()').get()
        item['size'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--attribute_pa_size > td'
        ).xpath('.//text()').get()
        item['color'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--secondary-color > td'
        ).xpath('.//text()').get()
        item['material'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--attribute_pa_material > td'
        ).xpath('.//text()').get()
        item['hardware'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--secondary-hardware > td'
        ).xpath('.//text()').get()
        item['year'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--year > td'
        ).xpath('.//text()').get()
        item['condition'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--condition-rating > td'
        ).xpath('.//text()').get()
        item['measurements'] = shop_attributes.css(
            '.woocommerce-product-attributes-item--measurements > td'
        ).xpath('.//text()').get()

        images = response.css('.summary-before')
        images = images.css('img').xpath('@src').getall()
        images = ['https:' + image for image in images]
        item['images'] = images

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        self.logger.info("Crawling URL done: %s", item)
        yield item
