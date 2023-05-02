# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import time
from os import getenv

import pika
import pymongo

# useful for handling different item types with a single interface


class BagPipeline:
    custom_settings = {
        'LOG_FILE': 'log/crawling_content.log',
    }

    def __init__(self):
        # Load env variables
        self.mongo_host = getenv('MONGO_CONNECTION_STRING')
        self.database_name = getenv('MONGO_DBNAME', 'kl_bag_ranking')
        self.collection_name = getenv('MONGO_COLLECTION', 'bag_raw')

        self.client = pymongo.MongoClient(self.mongo_host)
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]
        self.collection.create_index('link', unique=True)

    def process_item(self, item, spider):
        spider.logger.info('processing item')

        # check if duplicate in db
        existing_item = self.collection.find_one({"link": item['link']})
        if existing_item:
            existing_item['last_update'] = time.strftime(
                "%Y-%m-%d", time.localtime())
            # update item in db
            self.collection.update_one(
                {"link": item['link']}, {"$set": dict(existing_item)})
            spider.logger.info('Item updated in MongoDB')
            return item

        # add crawl date
        item['crawl_date'] = time.strftime("%Y-%m-%d", time.localtime())
        # add flag
        item['is_AI'] = False
        # insert to db
        result = self.collection.insert_one(dict(item))
        spider.logger.info(
            'Item added to MongoDB with id %s', result.inserted_id)
        return item


class CrawlingLinkPipeline:
    custom_settings = {
        'LOG_FILE': 'log/crawling_link.log',
    }

    def __init__(self):
        self.rabbitmq_host = getenv('RABBITMQ_HOST', 'localhost')
        self.rabbitmq_username = getenv('RABBITMQ_USERNAME')
        self.rabbitmq_password = getenv('RABBITMQ_PASSWORD')

        credentials = pika.PlainCredentials(
            self.rabbitmq_username,
            self.rabbitmq_password,
        )
        self.rabbitmq_exchange = getenv(
            'RABBITMQ_EXCHANGE', 'bag_ranking_crawl_link')
        self.rbmq_queue = getenv('RABBITMQ_QUEUE', 'bag_ranking_crawl_link')
        self.rbmq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.rabbitmq_host,
                credentials=credentials if self.rabbitmq_username else None,
            ),
        )
        self.rbmq_channel = self.rbmq_connection.channel()
        self.rbmq_channel.exchange_declare(
            exchange=self.rabbitmq_exchange,
            exchange_type='x-message-deduplication',
            arguments=dict({'x-cache-size': '5'}),
        )

    def process_item(self, item, spider):
        routing_key = self.rbmq_queue + "_" + item['website_name']
        queue_name = self.rbmq_queue + "_" + item['website_name']
        self.rbmq_channel.queue_declare(
            queue=queue_name,
        )
        self.rbmq_channel.queue_bind(queue_name, self.rabbitmq_exchange)
        self.rbmq_channel.basic_publish(
            exchange=self.rabbitmq_exchange,
            routing_key=routing_key,
            body=json.dumps(dict(item)),
            properties=pika.BasicProperties(
                headers={'x-deduplication-header': item['link']},
            ),
        )
        spider.logger.info(f" [x] Sent {dict(item)}")
        return item
