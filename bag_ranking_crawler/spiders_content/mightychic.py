import json

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
    name = "mightychic_content"
    queue_name = 'bag_ranking_crawl_link_mightychic'

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
        item['website_name'] = 'mightychic'

        item['link'] = response.url

        title = response.css('h1.product-meta__title::text').get()
        price = response.css('.product-meta__price::text').get()

        description = response.css(
            ".product__description").xpath('.//text()').extract()
        measures = get_measurements(description)
        condition = get_condition(description)
        description = '\n'.join(description).strip()

        slides = response.css(".product__slideshow-slide")
        images = []
        for slide in slides:
            lmao = slide.xpath("@data-media-large-url").get()
            if lmao is not None and lmao is str:
                image = 'https:' + lmao
                images.append(image)

        is_sold = response.css(".label--sold-out").get()
        is_sold = is_sold is not None
        brand = response.css(".product-meta__vendor::text").get()

        item['title'] = title
        item['price'] = price
        item['description'] = description
        item['is_sold'] = is_sold
        item['images'] = images

        if len(images):
            item['thumbnail'] = images[0]

        item['brand'] = brand
        item['measurements'] = measures
        item['condition'] = condition

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
