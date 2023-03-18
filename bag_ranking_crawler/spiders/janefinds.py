import scrapy
from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "janefinds"
    start_urls = [
        "https://janefinds.com/collections/hermes?page={}".format(i) for i in range(1, 100)]

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = response.css(".product-item")
        for product in products:
            link = 'https://janefinds.com' + \
                product.css("a").xpath("@href").get()
            title = product.css(
                ".product-item__title").xpath('.//text()').get()

            price = product.css('.product__price--original')
            if price is not None:
                price = price.xpath('.//text()').get()
            else:
                price = None
            thumbnail = 'https:' + product.css('img').xpath("@src").get()
            item = BagRankingCrawlerItem()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']
        desc = response.css(
            '.product__description-inner').xpath('.//text()').getall()
        item['description'] = desc
        images = response.css('css-slider')
        images = images.css('img').xpath('@src').getall()
        images = ['https:' + image for image in images]
        item['images'] = images
        yield item
