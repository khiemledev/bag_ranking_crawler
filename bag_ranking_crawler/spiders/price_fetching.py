import scrapy
from ..items import BagPriceCrawlerItem
import pymongo
import time


class ProductSpider(scrapy.Spider):
    name = "price_fetching"
    custom_settings = {
        'ITEM_PIPELINES': {
            'bag_ranking_crawler.pipelines.PricePipeline': 300
        }
    }

    def start_requests(self):
        client = pymongo.MongoClient(
            "mongodb://admin:Embery#1234@51.161.130.170:27017")
        db = client['bag_ranking']
        collection = db['bags']
        links = collection.find({}, {'link': 1, 'source': 1})
        for link in links:
            yield scrapy.Request(url=link['link'], callback=self.parse, meta={'source': link['source'], 'bag_id': link['_id']})

    def parse(self, response):
        meta = response.meta
        source = meta['source']
        bag_id = meta['bag_id']
        price = None
        if source == 'bjluxury':
            price = ' '.join(response.css(
                '.woocommerce-Price-amount.amount').css('::text').extract())
        if source == 'farfetch':
            price = ' '.join(response.xpath(
                '//*[@id="content"]/div/div[1]/div[2]/div/div/div[2]/div[2]/p[1]').css('::text').extract())
        if source == 'ginzaxiaoma':
            url = response.url
            product_id = url.split('/')[-1]
            yield scrapy.Request(url='https://ginzaxiaoma.com/mall-portal/pms/product/'+product_id, callback=self.ginzaxiaoma_parse, meta={'bag_id': bag_id})
        if source == 'janefinds':
            price = ' '.join(response.css(
                '.product__price--original::text').extract())
        if source == 'lilacblue':
            product_id = response.url.split('/')[-1]
            price = ' '.join(response.xpath(
                '//*[@id="content"]/div[4]/div[2]/div/p/span').css('::text').extract())
        if source == 'loveluxury':
            price = ' '.join(response.xpath(
                '//*[@id="content"]/div[2]/div/div[1]/div[2]/div/div[3]/div/p/span').css('::text').extract())
        if source == 'mightychic':
            price = response.xpath('//*[@id="main"]/div[1]/div/div/div/div[2]/div[2]/div[1]/div[1]/span').css('::text').get()
        if source =='vestiairecollective':
            price = response.xpath('//*[@id="__next"]/div/main/div[1]/div[4]/div/div[1]/div/div[2]/div/p[1]/span').css('::text').get()

        if price == None or price == '':
            return
        item = BagPriceCrawlerItem()
        item['price'] = price
        item['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item['bag_id'] = bag_id
        yield item

    def ginzaxiaoma_parse(self, response):
        meta = response.meta
        bag_id = meta['bag_id']
        price = None

        data = response.json()
        price = str(data['data']['price']) + ' ' + data['data']['currency']
        item = BagPriceCrawlerItem()
        item['price'] = price
        item['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        item['bag_id'] = bag_id
        yield item
