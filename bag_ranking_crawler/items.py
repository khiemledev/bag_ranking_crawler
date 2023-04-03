# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BagRankingCrawlerItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    thumbnail = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()


class BagPriceCrawlerItem(scrapy.Item):
    price = scrapy.Field()
    date = scrapy.Field()
    bag_id = scrapy.Field()
    