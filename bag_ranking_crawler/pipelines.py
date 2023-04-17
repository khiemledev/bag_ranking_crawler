# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import time

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
        # check if duplicate in db
        existing_item = self.collection.find_one({"link": item['link']})
        if existing_item:
            return item
        # add crawl date
        item['crawl_date'] = time.strftime("%Y-%m-%d", time.localtime())
        # add flag
        item['is_AI'] = False
        # insert to db
        self.collection.insert_one(dict(item))
        return item
