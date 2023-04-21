# https://www.ebay.com/b/HERMES-Bags-Handbags-for-Women/169291/bn_99586694

import scrapy

from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "ebay"
    start_urls = [
        *["https://www.ebay.com/b/HERMES-Bags-Handbags-for-Women/169291/bn_99586694?rt=nc&_pgn={i}" for i in range(1, 28)],
    ]

    def parse(self, response):
        products = response.css(
            'div.s-item__wrapper')
        for prod in products:
            link = prod.css('a.s-item__link::attr(href)').get()
            # remove ?hash=item... from link
            link = link.split('?')[0]

            title = prod.css('h3.s-item__title::text').get()
            price = prod.css('span.s-item__price').xpath('.//text()').get()
            thumbnail = prod.css('img.s-item__image-img::attr(src)').get()

            item = BagRankingCrawlerItem()
            item['link'] = link
            item['title'] = title
            item['price'] = price
            item['thumbnail'] = thumbnail
            yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']

        if item['thumbnail'] == 'https://ir.ebaystatic.com/cr/v/c1/s_1x2.gif':
            item['thumbnail'] = response.css(
                'div.ux-image-carousel-item.active.image img::attr(src)').get()
        self.logger.info(item['thumbnail'])

        images = response.css(
            'button.ux-image-filmstrip-carousel-item.image-treatment img::attr(src)').getall()
        images = [i.replace('s-l64', 's-l500') for i in images]

        item['images'] = images
        yield item
