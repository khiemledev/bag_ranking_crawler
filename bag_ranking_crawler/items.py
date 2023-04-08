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
    crawl_date = scrapy.Field()
    is_AI = scrapy.Field()

    sold_date = scrapy.Field()

    brand = scrapy.Field()
    model = scrapy.Field()
    color = scrapy.Field()
    material = scrapy.Field()
    hardware = scrapy.Field()
    year = scrapy.Field()
    measurements = scrapy.Field()
    condition = scrapy.Field()