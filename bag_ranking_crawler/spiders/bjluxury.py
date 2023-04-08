import scrapy
from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "bjluxury"
    start_urls = [
        "https://bjluxury.com/all-hermes-bags/?product-page={}&count=36".format(i) for i in range(1, 500)]

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
                price = ' '.join(price.xpath('.//text()').getall())
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

        shop_attributes = response.css('.shop_attributes')
        item['brand'] = shop_attributes.css(
            'tr:nth-child(1) > td').xpath('.//text()').get()
        item['model'] = response.css(
            'tr:nth-child(2) > td').xpath('.//text()').get()
        item['color'] = response.css(
            'tr:nth-child(4) > td').xpath('.//text()').get()
        item['material'] = response.css(
            'tr:nth-child(5) > td').xpath('.//text()').get()
        item['hardware'] = response.css(
            'tr:nth-child(6) > td').xpath('.//text()').get()
        item['year'] = response.css(
            'tr:nth-child(7) > td').xpath('.//text()').get()
        item['measurements'] = response.css(
            'tr:nth-child(10) > td').xpath('.//text()').get()
        item['condition'] = response.css(
            'tr:nth-child(9) > td').xpath('.//text()').get()

        images = response.css('.summary-before')
        images = images.css('img').xpath('@src').getall()
        images = ['https:' + image for image in images]
        item['images'] = images
        yield item
