import scrapy


class SellierknightsbridgeSpider(scrapy.Spider):
    name = 'sellierknightsbridge'
    allowed_domains = ['www.sellierknightsbridge.com']
    start_urls = ['http://www.sellierknightsbridge.com/']

    def parse(self, response):
        pass
