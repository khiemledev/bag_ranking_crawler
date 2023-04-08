import scrapy
from ..items import BagRankingCrawlerItem
import re


class ProductSpider(scrapy.Spider):
    name = "lilacblue"
    start_urls = [
        "https://lilacblue.com/product-category/hermes-birkin-kelly-bags/calf-leather-exotic-birkins/", "https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-kelly-bags/",
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
            link = product.css('.product-title a').xpath('@href').get()
            price = product.css(
                '.price').xpath('.//text()').extract()
            price = ''.join(price).strip()
            thumbnail = product.css('.wp-post-image').xpath("@src").get()
            item = BagRankingCrawlerItem()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            if link is not None:
                yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']
        desc = response.css(".post-content").xpath('.//text()').getall()
        desc = ' '.join(desc).replace('\xa0','')
        item['description'] = desc
        size_re = re.compile(r'Dimensions\s*:\s*(.+)')
        color_re = re.compile(r'(Hermes )?Colour\s*:\s*(.+)')
        hardware_re = re.compile(r'Hardware\s*:\s*(.+)')
        material_re = re.compile(r'Leather\s*:\s*(.+)')
        condition_re = re.compile(r'Condition\s*:\s*(.+)')

        color = color_re.search(desc)
        if color is not None:
            color = color.group(2)
        else:
            color = None
        size = size_re.search(desc)
        if size is not None:
            size = size.group(1)
        else:
            size = None



        hardware = hardware_re.search(desc)
        if hardware is not None:
            hardware = hardware.group(1)
        else:
            hardware = None

        material = material_re.search(desc)
        if material is not None:
            material = material.group(1)
        else:
            material = None

        condition = condition_re.search(desc)
        if condition is not None:
            condition = condition.group(1)
        else:
            condition = None
        item['measurements'] = size.strip()
        item['color'] = color.strip()
        item['hardware'] = hardware.strip()
        item['material'] = material.strip()
        item['condition'] = condition.strip()
        item['description'] = desc.strip()

        yield item
