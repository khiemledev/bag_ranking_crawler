import scrapy
from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "bjluxury"
    start_urls = [
        "https://bjluxury.com/all-hermes-bags/?product-page={}&count=36".format(i) for i in range(1, 2)]

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = response.css(".product")
        for product in products:
            link = product.css("a").xpath("@href").get()
            title = product.css(
                ".woocommerce-loop-product__title").xpath('.//text()').get()
            price = product.css('.woocommerce-Price-amount')
            if price is not None:
                price = price.xpath('.//text()').getall()
            else:
                price = None
            thumbnail = product.css('.wp-post-image').xpath("@src").get()
            item = BagRankingCrawlerItem()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']
        desc = response.css('.woocommerce-product-attributes').xpath('.//text()').getall()
        item['description'] = desc
        images = response.css('.summary-before')
        images = images.css('img').xpath('@src').getall()
        images = ['https:' + image for image in images]
        item['images'] = images
        yield item
