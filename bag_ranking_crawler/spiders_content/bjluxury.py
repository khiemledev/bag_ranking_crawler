import json
from os import getenv

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


def _strip(v):
    if v is None:
        return
    v = v.strip()
    if v == '':
        return
    return v

class ProductSpider(scrapy.Spider):
    name = "bjluxury_content"
    queue_name = 'bag_ranking_crawl_link_bjluxury'

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.BagPipeline": 300,
        },
        "RABBITMQ_HOST": getenv('RABBITMQ_HOST', ''),
        "RABBITMQ_USERNAME": getenv('RABBITMQ_USERNAME', ''),
        "RABBITMQ_PASSWORD": getenv('RABBITMQ_PASSWORD', ''),
    }

    def start_requests(self):
        credentials = pika.PlainCredentials(
            self.settings.get('RABBITMQ_USERNAME'),
            self.settings.get('RABBITMQ_PASSWORD'),
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                # host='localhost',
                host=self.settings.get('RABBITMQ_HOST'),
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
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'method_frame': method_frame},
            )

    def parse(self, response):
        item = BagRankingCrawlerItem()
        item['website_name'] = 'bjluxury'

        item['link'] = response.url

        title = response.css('.product_title').xpath('.//text()').get()
        item['title'] = _strip(title)

        price = response.css('.woocommerce-Price-amount.amount').xpath('.//text()').get()
        item['price'] = _strip(price)

        if not item['price']:
            item['is_sold'] = True
        else:
            item['is_sold'] = False

        shop_attributes = response.css('.shop_attributes')

        brand = shop_attributes.css(
            '.woocommerce-product-attributes-item--brand > td'
        ).xpath('.//text()').get()
        item['brand'] = _strip(brand)

        model = shop_attributes.css(
            '.woocommerce-product-attributes-item--attribute_pa_model > td'
        ).xpath('.//text()').get()
        item['model'] = _strip(model)

        size = shop_attributes.css(
            '.woocommerce-product-attributes-item--attribute_pa_size > td'
        ).xpath('.//text()').get()
        item['size'] = _strip(size)

        color = shop_attributes.css(
            '.woocommerce-product-attributes-item--secondary-color > td'
        ).xpath('.//text()').get()
        item['color'] = _strip(color)

        material = shop_attributes.css(
            '.woocommerce-product-attributes-item--attribute_pa_material > td'
        ).xpath('.//text()').get()
        item['material'] = _strip(material)

        hardware = shop_attributes.css(
            '.woocommerce-product-attributes-item--secondary-hardware > td'
        ).xpath('.//text()').get()
        item['hardware'] = _strip(hardware)

        year = shop_attributes.css(
            '.woocommerce-product-attributes-item--year > td'
        ).xpath('.//text()').get()
        item['year'] = _strip(year)

        condition = shop_attributes.css(
            '.woocommerce-product-attributes-item--condition-rating > td'
        ).xpath('.//text()').get()
        item['condition'] = _strip(condition)

        measures = shop_attributes.css(
            '.woocommerce-product-attributes-item--measurements > td'
        ).xpath('.//text()').get()
        item['measurements'] = _strip(measures)

        images = response.css('.summary-before')
        images = images.css('img').xpath('@src').getall()
        images = ['https:' + image for image in images]
        item['images'] = images

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
