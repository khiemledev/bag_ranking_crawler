import scrapy
from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "lilacblue"
    start_urls = [
        "https://lilacblue.com/product-category/hermes-birkin-kelly-bags/calf-leather-exotic-birkins/"
,"https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-kelly-bags/",
'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-bolide-evelyne-new/',
'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-constance-and-others/',
'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-picotin-new/',
'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-lindy-new/',
'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-herbag-new/',
    'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-jige-garden-party-more/'
    ]

    def parse(self, response):
        # Extract product information
        products = response.css(".product")
        for product in products:
            title = product.css(
                ".product-title").css('a').xpath('.//text()').get()
            link = product.css('.product-title').css('a').xpath('@href').get()
            price = product.css(
                '.price').xpath('.//text()').extract()
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
        description = response.css(
            ".woocommerce-Tabs-panel--description").xpath('.//text()').extract()
        description = ' '.join(description).strip()
        item['description'] = description

        yield item
