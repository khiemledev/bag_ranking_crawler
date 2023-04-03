# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from typing import TypedDict


class PriceHistory(TypedDict):
    price: str
    date: str
    bag_id: str


class PricePipeline:

    def __init__(self):
        self.client = pymongo.MongoClient(
            "mongodb://admin:Embery#1234@51.161.130.170:27017")
        database_name = 'bag_ranking'
        self.db = self.client[database_name]
        self.collection = self.db['price_history']

    def process_item(self, item, spider):
        price_history = PriceHistory()
        price_history['price'] = item['price']
        price_history['date'] = item['date']
        price_history['bag_id'] = item['bag_id']
        self.collection.insert_one(price_history)
        return item