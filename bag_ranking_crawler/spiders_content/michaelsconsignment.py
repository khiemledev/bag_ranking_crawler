import json
import re
from os import getenv

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


def get_measurements(desc):
    measurements = []
    # lines = desc.split('\n')
    lines = desc
    i = 0
    while i < len(lines):
        if lines[i].strip() == '':
            del lines[i]
            continue
        i += 1
    lines.append('\n')
    for i in range(len(lines) - 1):
        line = lines[i]
        if "measurement" in line.lower():
            for j in range(i+1, len(lines)):
                line2 = lines[j].strip().lower()
                if line2 == '' or \
                    'condition' in line2 or\
                    'material' in line2 or\
                    'hardware' in line2 or\
                        'color' in line2:
                    break
                measurements.append(line2)

    return '\n'.join(measurements)

class ProductSpider(scrapy.Spider):
    name = "michaelsconsignment_content"
    queue_name = 'bag_ranking_crawl_link_michaelsconsignment'

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
        item['link'] = response.url
        item['website_name'] = 'michaelsconsignment'

        brand = response.css('.detail .vendor a::text').get()
        item['brand'] = brand

        title = response.css('h1.title::text').get()
        item['title'] = title.strip() if title is not None else None

        price = response.css('.price-area .current-price::text').get()
        price = price.strip() if price is not None else None
        if price and price.lower() == 'sold out':
            item['is_sold'] = True
            item['price'] = None
        else:
            item['is_sold'] = False
            item['price'] = price

        images = response.css('a.thumbnail::attr(href)').getall()
        images = ['http:' + img for img in images]
        item['images'] = images
        if len(images):
            item['thumbnail'] = images[0]

        raw_desc = response.css('.with-icon__beside').xpath(".//text()").extract()
        desc = raw_desc[0]
        for i in range(1, len(raw_desc)):
            l = raw_desc[i-1].strip().lower()
            r = raw_desc[i].replace(' :', ':')

            if 'hardware' in l or\
                'color' in l or\
                'condition' in l:
                desc += r.strip()
                continue

            desc += '\n' + r.strip()

        item['description'] = desc

        hardware_re = re.compile('Hardware:(.*)')
        hardware = hardware_re.search(desc)
        if hardware:
            hardware = hardware.group(1).strip()
        item['hardware'] = hardware

        color_re = re.compile('Color:(.*)')
        color = color_re.search(desc)
        if color:
            color = color.group(1).strip()
        item['color'] = color

        condition_re = re.compile('Condition:(.*)')
        condition = condition_re.search(desc)
        if condition:
            condition = condition.group(1).strip()
        item['condition'] = condition

        measures = get_measurements(raw_desc)
        item['measurements'] = measures

        # self.channel.basic_ack(
        #     delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
