import json
import re

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "ounass_content"
    queue_name = 'bag_ranking_crawl_link_ounass'

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
        item['website_name'] = 'ounass'

        item['link'] = response.url

        title = response.css('h1.PDPDesktop-name span::text').get()
        item['title'] = title.strip() if title is not None else None

        price = response.css('.PriceContainer-price::text').get()
        item['price'] = price.strip() if price is not None else None

        tabs = response.css('#content-tab-list button')
        for tab in tabs:
            tab_num = tab.css('::attr(id)').get().split('-')[-1]
            tab_label = tab.css('::text').get().strip()

            content = response.css('#content-tab-panel-' + tab_num).xpath(".//text()").extract()
            content = ''.join(content)

            if tab_label == "Editor's advice":
                item['description'] = content + '\n'
                continue

            if tab_label == 'Size & Fit':
                item['measurements'] = content
                continue

            if tab_label == 'Design details':
                if 'description' in item and item['description'] is not None:
                    item['description'] += content
                else:
                    item['description'] = content

                color_re = re.compile('Colour: (.*)')
                color = color_re.search(content)
                if color:
                    color = color.group(1).strip()
                    item['color'] = color

                hardware_re = re.compile('.*hardware.*', re.IGNORECASE)
                hardware = hardware_re.search(content)
                if hardware:
                    hardware = hardware.group(0).strip()
                    item['hardware'] = hardware

                condition_re = re.compile('.*condition.*', re.IGNORECASE)
                condition = condition_re.search(content)
                if condition:
                    condition = condition.group(0).strip()
                    item['condition'] = condition
                continue

        images = response.css('picture[itemprop="image"] source::attr(srcset)').getall()
        images = ['https:' + img for img in images]
        # process image link to get bigger image
        def _process_img_link(link):
            dw_idx = link.find('dw=')
            if dw_idx != -1:
                # Find the content between "dw=" and the first ","
                start = dw_idx + 3
                end = link.find(",", start)
                if end == -1:
                    end = len(link)
                query = link[start-3:end]
                link = link.replace(query, 'dw=1024')

            dh_idx = link.find('dh=')
            if dh_idx != -1:
                # Find the content between "dh=" and the first ","
                start = dh_idx + 3
                end = link.find(",", start)
                if end == -1:
                    end = len(link)
                query = link[start-3:end]
                link = link.replace(query, 'dh=1024')

            return link

        item['images'] = [_process_img_link(img) for img in images]

        if len(images):
            item['thumbnail'] = images[0]

        # self.logger.info(item)

        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
