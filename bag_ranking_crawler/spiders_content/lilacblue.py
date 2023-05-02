import json
import re

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
    name = "lilacblue_content"
    queue_name = 'bag_ranking_crawl_link_lilacblue'

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
                # host='localhost',
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
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'method_frame': method_frame},
            )

    def parse(self, response):
        item = BagRankingCrawlerItem()
        item['website_name'] = 'lilacblue'

        item['link'] = response.url

        title = response.css('h2.product_title::text').get()
        item['title'] = _strip(title)

        price = response.css('.summary-container .price').xpath('.//text()').extract()
        price = ''.join(price)
        item['price'] = _strip(price)

        is_sold = response.css('.stock.out-of-stock::text').get()
        if is_sold and "already sold" in is_sold.lower():
            item['is_sold'] = True
        else:
            item['is_sold'] = False

        images = response.css(
            ".iconic-woothumbs-thumbnails__image::attr(src)").getall()
        images = ', '.join(images)

        desc = response.css(".post-content").xpath('.//text()').getall()
        desc = ' '.join(desc).replace('\xa0', '')
        item['description'] = desc
        size_re = re.compile(r'Dimensions\s*:\s*(.+)')
        color_re = re.compile(r'(Hermes )?Colour\s*:\s*(.+)')
        hardware_re = re.compile(r'Hardware\s*:\s*(.+)')
        material_re = re.compile(r'Leather\s*:\s*(.+)')
        condition_re = re.compile(r'Condition\s*:\s*(.+)')

        color = color_re.search(desc)
        if color is not None:
            color = color.group(2)
        else:
            color = None
        size = size_re.search(desc)
        if size is not None:
            size = size.group(1)
        else:
            size = None

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

        item['images'] = images

        if len(images):
            item['thumbnail'] = images[0]

        item['measurements'] = _strip(size)
        item['color'] = _strip(color)
        item['hardware'] = _strip(hardware)
        item['material'] = _strip(material)
        item['condition'] = _strip(condition)
        item['description'] = _strip(desc)

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
