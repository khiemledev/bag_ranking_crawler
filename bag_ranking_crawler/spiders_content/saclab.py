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
    name = "saclab_content"
    queue_name = 'bag_ranking_crawl_link_saclab'

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
        item['website_name'] = 'saclab'

        item['link'] = response.url

        brand = response.css('.product__title-brand a::text').get()
        item['brand'] = _strip(brand)

        title = response.css('.product__title::text').get()
        item['title'] = _strip(title)

        desc = response.css('.product__desc::text').get()
        item['description'] = _strip(desc)

        specs = response.css('.product__options-item')
        for spec in specs:
            prop = spec.css('.product__options-prop::text').get()
            value = spec.css('.product__options-val::text').get()

            if prop is None or value is None:
                continue

            prop = prop.lower()
            if 'size' in prop:
                item['measurements'] = _strip(value)
            elif 'color' in prop:
                item['color'] = _strip(value)

        price = response.css('.product__price').xpath('.//text()').extract()
        price = _strip(''.join(price))
        item['price'] = price

        images = response.css(
            '.f-carousel__slide-img::attr(src)').getall()
        item['images'] = images

        if len(images):
            item['thumbnail'] = images[0]

        is_sold = response.css('.product__sold-inner').get()
        is_sold = is_sold is not None
        item['is_sold'] = is_sold

        # self.logger.info(item)

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
