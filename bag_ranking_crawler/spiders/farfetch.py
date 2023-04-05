import scrapy
from ..items import BagRankingCrawlerItem
import json


class ProductSpider(scrapy.Spider):
    name = "farfetch"
    start_urls = [
        *["https://www.farfetch.com/vn/plpslice/listing-api/products-facets?page={}&view=90&scale=274&pagetype=Shopping&rootCategory=Women&pricetype=FullPrice&c-designer=70015".format(
            i) for i in range(1, 100)],
        *["https://www.farfetch.com/vn/plpslice/listing-api/products-facets?page={}&view=90&scale=274&pagetype=Shopping&rootCategory=Men&pricetype=FullPrice&c-designer=70015".format(i) for i in range(1, 100)],]

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = json.loads(response.body)['listingItems']['items']
        for product in products:
            title = product['shortDescription']
            price = product['priceInfo']['finalPrice']
            link = 'https://www.farfetch.com'+product['url']
            thumbnail = product['images']['model']
            item = BagRankingCrawlerItem()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']
        desc = response.css('.ltr-4y8w0i-Body').css('::text').getall()
        item['description'] = '\n'.join(desc)
        images = response.css('.e1dvjpls0')
        images = images.css('img').xpath('@src').getall()
        item['images'] = images
        yield item
