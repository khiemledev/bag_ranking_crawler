import json

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
    name = "loveluxury_content"
    queue_name = 'bag_ranking_crawl_link_loveluxury'

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
        item['website_name'] = 'loveluxury'

        item['link'] = response.url

        title = response.css('h2.product_title::text').get()
        item['title'] = title

        price = response.css(
            '.single-product-price .price .woocommerce-Price-amount.amount:first-child').xpath('.//text()').extract()
        price = ''.join(price).strip()
        item['price'] = price

        is_sold = response.css('.out-of-stock-prod').xpath('.//text()').extract()
        is_sold = ''.join(is_sold).strip().lower()

        if is_sold == 'sold out':
            item['is_sold'] = True
        else:
            item['is_sold'] = False

        description = response.css(".description").xpath('.//text()').extract()
        description = ' '.join(description).strip()
        item['description'] = description

        slides = response.css(".img-thumbnail")
        images = slides.css('img').xpath('@src').extract()
        item['images'] = images

        if len(images):
            item['thumbnail'] = images[0]

        tabs = [t.css("::text").get().strip()
                for t in response.css(".resp-tabs-list li")]
        resp_tabs = [r.css("::text").extract()
                     for r in response.css('.resp-tabs-container > .tab-content')]
        for tab, resp in zip(tabs, resp_tabs):
            if tab.lower() != 'size':
                continue
            _resp = '\n'.join([r.strip() for r in resp]).strip()
            item['measurements'] = _resp

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
