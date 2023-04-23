# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import time

import pika
import pymongo

# useful for handling different item types with a single interface


class BagPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient(
            "mongodb://admin:Embery#1234@51.161.130.170:27017")
        database_name = 'kl_bag_ranking'
        self.db = self.client[database_name]
        self.collection = self.db['bag_raw']
        self.collection.create_index('link', unique=True)

    def process_item(self, item, spider):
        spider.logger.info('processing item')

        # check if duplicate in db
        existing_item = self.collection.find_one({"link": item['link']})
        if existing_item:
            item['last_update'] = time.strftime("%Y-%m-%d", time.localtime())
            # update item in db
            self.collection.update_one(
                {"link": item['link']}, {"$set": dict(item)})
            spider.logger.info('Item updated in MongoDB')
            return item

        # add crawl date
        item['crawl_date'] = time.strftime("%Y-%m-%d", time.localtime())
        # add flag
        item['is_AI'] = False
        # insert to db
        # result = self.collection.insert_one(dict(item))
        # spider.logger.info(
        #     'Item added to MongoDB with id %s', result.inserted_id)
        return item


class CrawlingPipeline:
    def __init__(self):
        self.rbmq_queue = 'bag_ranking_crawl_link'
        self.rbmq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.rbmq_channel = self.rbmq_connection.channel()
        self.rbmq_channel.queue_declare(
            queue=self.rbmq_queue,
        )

    def process_item(self, item, spider):
        routing_key = self.rbmq_queue + "_" + item['website_name']
        self.rbmq_channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=json.dumps(dict(item)),
        )
        spider.logger.info(f" [x] Sent {dict(item)}")
        return item
