import re

import scrapy

from ..items import BagRankingCrawlerItem

base_url = "https://mightychic.com/collections/all-hermes-bags?view=infinite-scroll"


def get_measurements(desc):
    measurements = []
    # lines = desc.split('\n')
    lines = desc
    lines.append('\n')
    for i in range(len(lines) - 1):
        line = lines[i]
        if "bag measures:" in line.lower():
            for j in range(i+1, len(lines)):
                line2 = lines[j].strip()
                if line2 == '' or "condition:" in line2.lower():
                    break
                measurements.append(line2)

    return '\n'.join(measurements)


def get_condition(desc):
    measurements = []
    # lines = desc.split('\n')
    lines = desc
    lines.append('\n')
    for i in range(len(lines) - 1):
        line = lines[i]
        if "condition:" in line.lower():
            for j in range(i+1, len(lines)):
                line2 = lines[j].strip()
                if line2 == '' or "bag measures:" in line2.lower():
                    break
                measurements.append(line2)

    return '\n'.join(measurements)


class ProductSpider(scrapy.Spider):
    name = "mightychic"
    start_urls = [f"{base_url}&page=1"]

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = response.css(".collection__item")
        for product in products:
            title = product.css("h2").xpath(".//a/text()").get()
            link = 'https://mightychic.com' + \
                product.css("h2").xpath(".//a/@href").get()
            price = product.xpath(
                ".//span[@class='product-item__price']/text()").get()
            thumbnail = 'https:' + \
                product.css('img').xpath(
                    "@data-src").get().replace('{width}', '1600')
            item = BagRankingCrawlerItem()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            yield response.follow(url=link, callback=self.product_parse, meta={'item': item})
        next_page = len(products) > 0
        if next_page:
            next_page_url = response.urljoin(
                f"{base_url}&page={int(response.url.split('=')[-1]) + 1}")
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def product_parse(self, response):
        item = response.meta['item']
        description = response.css(
            ".product__description").xpath('.//text()').extract()
        measures = get_measurements(description)
        condition = get_condition(description)
        description = '\n'.join(description).strip()

        slides = response.css(".product__slideshow-slide")
        images = []
        for slide in slides:
            lmao = slide.xpath("@data-media-large-url").get()
            if lmao is not None and lmao is str:
                image = 'https:' + lmao
                images.append(image)

        is_sold = response.css(".label--sold-out").get()
        is_sold = is_sold is not None
        brand = response.css(".product-meta__vendor::text").get()

        item['description'] = description
        item['is_sold'] = is_sold
        item['images'] = images
        item['brand'] = brand
        item['measurements'] = measures
        item['condition'] = condition

        # self.logger.info(item)
        yield item
