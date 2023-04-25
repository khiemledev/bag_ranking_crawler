import json
from urllib.parse import parse_qs, urlparse

import pika
import scrapy

from bag_ranking_crawler.items import BagRankingCrawlerItem


def get_pdp(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    # get the first value of the 'pdp' parameter or None if not found
    pdp_param = query_params.get('pdp', [None])[0]
    return pdp_param


class ProductSpider(scrapy.Spider):
    name = "thevintagebar_content"
    queue_name = 'bag_ranking_crawl_link_thevintagebar'

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

            pdp = get_pdp(url)
            if not pdp:
                continue

            url = f"https://catalog.thevintagebar.com/client/pdp/{pdp}/lang/en/currency/eur"

            self.logger.info("Crawling URL get from RabbitMQ: %s", url)
            yield scrapy.Request(url=url, callback=self.parse, meta={'method_frame': method_frame})

    def parse(self, response):
        item = BagRankingCrawlerItem()
        item['website_name'] = 'thevintagebar'

        item['link'] = response.url

        # parse json response
        data = json.loads(response.body)

        item['title'] = data['name']
        item['description'] = data['description']
        item['measurements'] = data['measurement']
        item['price'] = str(data['price']) + data['base_currency']
        item['material'] = data['material']
        item['color'] = ', '.join([c['value'] for c in data['colors']])
        item['thumbnail'] = data['image_url']
        item['brand'] = data['brand_name']
        item['condition'] = f"Rating: {data['condition_rating']} - {data['condition_description']}"
        if data['stock'] > 0:
            item['is_sold'] = False
        else:
            item['is_sold'] = True
        item['images'] = [i['original_url'] for i in data['media_entities']]
        # self.logger.info('crawled iten: %s', item)
        self.channel.basic_ack(
            delivery_tag=response.meta['method_frame'].delivery_tag)
        yield item
