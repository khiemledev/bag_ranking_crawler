import json
import re

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "madisonavenuecouture_content"
    queue_name = 'bag_ranking_crawl_link_madisonavenuecouture'

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
                host='localhost',
                # host='rabbitmq.embery.com.au',
                # credentials=credentials,
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
        item['website_name'] = 'madisonavenuecouture'

        item['link'] = response.url

        title = response.css('h1.product-title::text').get()
        item['title'] = title.strip() if title else None

        price = response.css('.prices .price .money::text').get()
        price = price.strip() if price else None
        currency = response.css('.prices .price .money::attr(data-currency)').get()
        if currency:
            price += ' - ' + currency
        item['price'] = price

        condition = response.css('.product-condition::text').get()
        item['condition'] = condition.strip().replace('Condition: ', '') if condition else None

        tabs = response.css('.wrapper-tab-content')
        for tab in tabs:
            tab_title = tab.css('.tab-title a.tab-links').xpath('.//text()').extract()
            tab_title = ' '.join(tab_title).strip()
            tab_content = tab.css('.tab-content').xpath('.//text()').extract()
            tab_content = ' '.join([t.strip() for t in tab_content]).strip()
            if 'description' in tab_title.lower():
                item['description'] = tab_content
                break

        images = response.css('.product-img-box a::attr(data-image)').getall()
        images = ['https:' + i for i in images]
        item['images'] = images

        if len(images) > 0:
            item['thumbnail'] = images[0]

        measures_re = re.compile('Measurements: (.*)')
        measures = measures_re.search(item['description'])
        if measures:
            measures = measures.group(1)
        item['measurements'] = measures

        condition_re = re.compile('Condition: (.*)')
        dondition = condition_re.search(item['description'])
        if dondition:
            dondition = dondition.group(1)
        item['condition'] = dondition


        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
