import json

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "farfetch_content"
    queue_name = 'bag_ranking_crawl_link_farfetch'

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
        item = BagRankingCrawlerItem()
        item['link'] = response.meta['link']

        title = response.css(
            'p[data-testid="product-short-description"]').xpath(".//text()").get()
        price = response.css(
            'p[data-component="PriceLarge"]').xpath(".//text()").get()
        thumbnail = response.css('img.ltr-1w2up3s').xpath('@src').get()

        item['title'] = title
        item['price'] = price
        item['thumbnail'] = thumbnail
        desc = response.css('.ltr-4y8w0i-Body').css('::text').getall()
        item['description'] = '\n'.join(desc)
        images = response.css('.e1dvjpls0')
        images = images.css('img').xpath('@src').getall()
        item['images'] = images

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        self.logger.info("Crawled item: %s", item)
        yield item
