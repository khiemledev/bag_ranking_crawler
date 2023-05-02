import json
from os import getenv

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


def get_measurements(desc):
    measurements = []
    # lines = desc.split('\n')
    lines = desc
    lines.append('\n')
    for i in range(len(lines) - 1):
        line = lines[i]
        if "bag measures:" in line.lower():
            for j in range(i+1, len(lines)):
                line2 = lines[j].strip()
                if line2 == '' or "condition:" in line2.lower():
                    break
                measurements.append(line2)

    return '\n'.join(measurements)


def get_condition(desc):
    measurements = []
    # lines = desc.split('\n')
    lines = desc
    lines.append('\n')
    for i in range(len(lines) - 1):
        line = lines[i]
        if "condition:" in line.lower():
            for j in range(i+1, len(lines)):
                line2 = lines[j].strip()
                if line2 == '' or "bag measures:" in line2.lower():
                    break
                measurements.append(line2)

    return '\n'.join(measurements)


class ProductSpider(scrapy.Spider):
    name = "worldsbest_content"
    queue_name = 'bag_ranking_crawl_link_worldsbest'

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
            yield scrapy.Request(url=url, callback=self.parse, meta={'method_frame': method_frame})

    def parse(self, response):
        item = BagRankingCrawlerItem()
        item['website_name'] = 'worldsbest'

        item['link'] = response.url

        title = response.css('h1.product-title::attr(content)').get()
        item['title'] = title

        brand = response.css('div.product-brand::text').get()
        item['brand'] = brand

        price = response.css('.current-price').xpath(".//text()").extract()
        price = ''.join(price)
        item['price'] = price

        desc_raw = response.css(
            '.product-desc-inner').xpath(".//text()").extract()

        measures = get_measurements(desc_raw).strip()
        item['measurements'] = measures if measures != '' else None

        condition = get_condition(desc_raw).strip()
        item['condition'] = condition if condition != '' else None

        desc = '\n'.join(desc_raw)
        item['description'] = desc

        # get all src attr from a element deep nested inside
        images = response.css(
            '.cloud-zoom-gallery-thumbs img').xpath("@src").getall()
        item['images'] = images

        if len(images):
            item['thumbnail'] = images[0]

        details = response.css('.detail')
        measures = ''
        for detail in details:
            label = detail.css('.detail-label::text').get()
            value = detail.css('.detail-desc::text').get()
            self.logger.info("Label: %s, Value: %s", label, value)
            if label is None or value is None:
                continue

            label = label.strip().lower()
            value = value.strip()
            if 'material' in label:
                item['material'] = value
            elif 'color' in label:
                item['color'] = value
            elif 'brand' in label:
                if item['brand'] is None:
                    item['brand'] = value
            elif 'height' in label:
                measures += 'Height: ' + value + '\n'
            elif 'width' in label:
                measures += 'Height: ' + value + '\n'
            elif 'depth' in label:
                measures += 'Height: ' + value + '\n'

        if item['measurements'] is None and measures != '':
            item['measurements'] = measures

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
