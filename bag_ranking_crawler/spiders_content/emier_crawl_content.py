import json
import re

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
                        'colour' in line2:
                    break
                measurements.append(line2)

    return '\n'.join(measurements)


class ProductSpider(scrapy.Spider):
    name = "emier_content"
    queue_name = 'bag_ranking_crawl_link_emier'

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
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'method_frame': method_frame},
            )

    def parse(self, response):
        item = BagRankingCrawlerItem()
        item['website_name'] = 'emier'

        item['link'] = response.url

        title = response.css('h1.ProductMeta__Title::text').get()
        item['title'] = title

        brand = response.css('h2.ProductMeta__Vendor').xpath('.//text()').get()
        item['brand'] = brand

        price = response.css('.ProductMeta__Price').xpath(
            ".//text()").extract()
        price = ''.join(price)
        item['price'] = price

        if price and price.lower() == 'sold':
            item['is_sold'] = True
        else:
            item['is_sold'] = False

        desc_raw = response.css(
            '.ProductMeta__Description').xpath(".//text()").extract()

        desc = ''.join(desc_raw)
        item['description'] = desc

        # get all src attr from a element deep nested inside
        images = response.css(
            '.Product__SlideItem--image img').xpath("@data-original-src").getall()
        item['images'] = images

        if len(images):
            item['thumbnail'] = images[0]

        measures = get_measurements(desc_raw)
        item['measurements'] = measures if measures != '' else None

        color_re = re.compile('Colour:(.+)')
        color = color_re.search(desc)
        if color is not None:
            color = color.group(1).strip()
        item['color'] = color

        material_re = re.compile('Material:(.+)')
        material = material_re.search(desc)
        if material is not None:
            material = material.group(1).strip()
        item['material'] = material

        hardware_re = re.compile('Hardware:(.+)')
        hardware = hardware_re.search(desc)
        if hardware is not None:
            hardware = hardware.group(1).strip()
        item['hardware'] = hardware

        condition_re = re.compile('Condition:(.+)')
        condition = condition_re.search(desc)
        if condition is not None:
            condition = condition.group(1).strip()
        item['condition'] = condition

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
