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
    name = "vestiairecollective_content"
    queue_name = 'bag_ranking_crawl_link_vestiairecollective'

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
        item['website_name'] = 'vestiairecollective'

        item['link'] = response.url

        brand = response.css(
            'a[class^="product-main-heading_productTitle__brand__link__"]::text').get()
        item['brand'] = brand

        title = response.css(
            'div[class^="product-main-heading_productTitle__name__"]::text').get()
        item['title'] = title

        # price = response.xpath(
        #     '//*[@id="__next"]/div/main/div[1]/div[4]/div/div[1]/div/div[2]/div').css('::text').getall()
        # price = ''.join(price).strip()
        price = response.css(
            'span[class^="product-price_productPrice__price"]::text').get()
        if price is None:
            price = response.css(
                'div[class="product-price_productPrice__YKAe0"]').xpath(".//text()").extract()
            price = ''.join(price).strip()

        sold_re = re.compile(r'Sold at\s*\$(.+)\son\s*(.+)')
        sold = sold_re.search(price)
        if sold is not None:
            item['sold_date'] = sold.group(2)

        images = response.css(
            'div[class^="p_productPage__top__image__k"]').css('img::attr(src)').getall()
        item['images'] = images

        li_list = response.xpath(
            '//*[@id="__next"]/div/main/section[1]/div/div/div[2]').css('li')
        desc = ''
        for li in li_list:
            desc += ''.join(li.css('::text').getall()) + '\n'

        condition_re = re.compile(r'Condition\s*:\s*(.+)')
        material_re = re.compile(r'Material\s*:\s*(.+)')

        if item['color'] is None:
            color_re = re.compile(r'Color\s*:\s*(.+)')
            color = color_re.search(desc)
            if color is not None:
                color = color.group(1)
            else:
                color = None

        if item['model'] is None:
            model_re = re.compile(r'Model\s*:\s*(.+)')
            model = model_re.search(desc)
            if model is not None:
                model = model.group(1)
            else:
                model = None

        material = material_re.search(desc)
        if material is not None:
            material = material.group(1)
        else:
            material = None

        condition = condition_re.search(desc)
        if condition is not None:
            condition = condition.group(1)
            condition = condition.replace("More info", "")
        else:
            condition = None

        item['material'] = material.strip() if material is not None else None
        item['condition'] = condition.strip(
        ) if condition is not None else None
        item['description'] = desc

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
