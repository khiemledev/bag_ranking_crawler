import re

import scrapy

from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "lilacblue"
    start_urls = [
        *[f"https://lilacblue.com/product-category/hermes-birkin-kelly-bags/calf-leather-exotic-birkins/page/{i}" for i in range(1, 43)],
        *[f"https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-kelly-bags/page/{i}" for i in range(1, 34)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-bolide-evelyne-new/page/{i}' for i in range(1, 3)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-constance-and-others/page/{i}' for i in range(1, 11)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-picotin-new/page/{i}' for i in range(1, 4)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-lindy-new/page/{i}' for i in range(1, 2)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-herbag-new/page/{i}' for i in range(1, 2)],
        *[f'https://lilacblue.com/product-category/hermes-birkin-kelly-bags/hermes-jige-garden-party-more/page/{i}' for i in range(1, 3)],
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
            thumbnail = product.css(
                '.featured-image > .wp-post-image').xpath("@src").get()
            item = BagRankingCrawlerItem()
            item['title'] = title.strip() if title is not None else None
            item['price'] = price.strip() if price is not None else None
            item['link'] = link.strip() if link is not None else None
            item['thumbnail'] = thumbnail.strip(
            ) if thumbnail is not None else None

            is_sold = product.css(
                'fusion-out-of-stock').xpath('.//text()').get()
            if is_sold is not None and is_sold.lower() == 'sold':
                item['is_sold'] = True
            else:
                item['is_sold'] = False

            if link is not None:
                yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']

        images = response.css(
            ".iconic-woothumbs-thumbnails__image::attr(src)").getall()
        images = ', '.join(images)

        desc = response.css(".post-content").xpath('.//text()').getall()
        desc = ' '.join(desc).replace('\xa0', '')
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

        item['images'] = images
        item['measurements'] = size.strip() if size is not None else None
        item['color'] = color.strip() if color is not None else None
        item['hardware'] = hardware.strip() if hardware is not None else None
        item['material'] = material.strip() if material is not None else None
        item['condition'] = condition.strip(
        ) if condition is not None else None
        item['description'] = desc.strip()

        yield item
