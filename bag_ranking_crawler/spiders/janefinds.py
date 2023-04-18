import re

import scrapy

from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "janefinds"
    start_urls = [
        "https://janefinds.com/collections/hermes?page={}".format(i) for i in range(1, 35)]

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = response.css(".product-item")
        for product in products:
            link = 'https://janefinds.com' + \
                product.css("a").xpath("@href").get()
            title = product.css(
                ".product-item__title").xpath('.//text()').getall()
            title = ' '.join(title).strip()
            price = product.css('.product__price--original')
            if price is not None:
                price = price.xpath('.//text()').get()
            else:
                price = None
            thumbnail = 'https:' + product.css('img').xpath("@src").get()

            is_sold = product.css(
                '.product-item__badge--sold').xpath(".//text()").get()
            if is_sold is not None and "sold" in is_sold.lower():
                is_sold = True
            else:
                is_sold = False

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
        desc = '\n'.join(desc)
        size_re = re.compile(r'Size: (.+)')
        color_re = re.compile(r'Color: (.+)')
        hardware_re = re.compile(r'Hardware: (.+)')
        material_re = re.compile(r'Material: (.+)')
        condition_re = re.compile(r'Condition: (.+)')

        size = size_re.search(desc)
        if size is not None:
            size = size.group(1)
        else:
            size = None

        color = color_re.search(desc)
        if color is not None:
            color = color.group(1)
        else:
            color = None

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
        item['measurements'] = size.strip() if isinstance(size, str) else None
        item['color'] = color.strip() if isinstance(color, str) else None
        item['hardware'] = hardware.strip() if isinstance(
            hardware, str) else None
        item['material'] = material.strip() if isinstance(
            material, str) else None
        item['condition'] = condition.strip() if isinstance(
            condition, str) else None
        item['description'] = desc
        images = response.css('css-slider')
        images = images.css('img').xpath('@src').getall()
        images = ['https:' + image for image in images]
        item['images'] = images
        yield item
