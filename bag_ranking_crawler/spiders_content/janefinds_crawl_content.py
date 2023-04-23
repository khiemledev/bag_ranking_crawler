import json
import re

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "janefinds_content"
    queue_name = 'bag_ranking_crawl_link_janefinds'

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
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    'method_frame': method_frame,
                    'link': url,
                },
            )

    def parse(self, response):
        link = response.meta['link']
        item = BagRankingCrawlerItem()

        title = response.css('.product__title').xpath('.//text()').get()
        price = response.css('.product__price').xpath('.//text()').get()

        item['title'] = title
        item['price'] = price
        item['link'] = link

        desc = response.css(
            '.product__description-inner').xpath('.//text()').getall()
        desc = '\n'.join(desc)
        size_re = re.compile(r'Size: (.+)')
        color_re = re.compile(r'Color: (.+)')
        hardware_re = re.compile(r'Hardware: (.+)')
        material_re = re.compile(r'Material: (.+)')
        condition_re = re.compile(r'Condition: (.+)')

        size = size_re.search(desc)
        if size is not None:
            size = size.group(1)
        else:
            size = None

        color = color_re.search(desc)
        if color is not None:
            color = color.group(1)
        else:
            color = None

        hardware = hardware_re.search(desc)
        if hardware is not None:
            hardware = hardware.group(1)
        else:
            hardware = None

        material = material_re.search(desc)
        if material is not None:
            material = material.group(1)
        else:
            material = None

        condition = condition_re.search(desc)
        if condition is not None:
            condition = condition.group(1)
        else:
            condition = None
        item['measurements'] = size.strip() if isinstance(size, str) else None
        item['color'] = color.strip() if isinstance(color, str) else None
        item['hardware'] = hardware.strip() if isinstance(
            hardware, str) else None
        item['material'] = material.strip() if isinstance(
            material, str) else None
        item['condition'] = condition.strip() if isinstance(
            condition, str) else None
        item['description'] = desc
        images = response.css('css-slider')
        images = images.css('img').xpath('@src').getall()
        images = ['https:' + image for image in images]
        item['images'] = images
        if len(images) > 0:
            item['thumbnail'] = images[0]

        self.logger.info(item)
        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
