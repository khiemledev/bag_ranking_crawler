import scrapy
from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "loveluxury"
    start_urls = [
        "https://loveluxury.co.uk/shop/hermes/page/{}".format(i) for i in range(1, 100)]

    def parse(self, response):
        # Extract product information
        products = response.css(".product-col")
        for product in products:
            title = product.css(
                ".woocommerce-loop-product__title").xpath('.//text()').get()
            link = product.css('.product-loop-title').xpath('@href').get()
            price = product.css(
                '.woocommerce-Price-amount').xpath('.//text()').extract()
            price = ''.join(price).strip()
            thumbnail = product.css('.wp-post-image').xpath("@src").get()
            item = BagRankingCrawlerItem()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']
        description = response.css(".description").xpath('.//text()').extract()
        description = ' '.join(description).strip()
        item['description'] = description

        slides = response.css(".img-thumbnail")
        images = slides.css('img').xpath('@src').extract()
        item['images'] = images
        yield item
