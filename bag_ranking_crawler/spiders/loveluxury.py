import scrapy

from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "loveluxury"
    start_urls = [
        *["https://loveluxury.co.uk/shop/hermes/page/{}".format(i) for i in range(1, 14)],
        *["https://loveluxury.co.uk/shop/chanel/page/{}".format(i) for i in range(1, 9)],
        *["https://loveluxury.co.uk/shop/louis-vuitton/page/{}".format(i) for i in range(1, 5)],
    ]

    def parse(self, response):
        url = response.url
        brand = url.split('/')[4]

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

            is_sold = product.css(".out-of-stock").get()
            is_sold = True if is_sold is not None else False

            item = BagRankingCrawlerItem()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            item['brand'] = brand
            yield response.follow(url=link, callback=self.product_parse, meta={'item': item, })

    def product_parse(self, response):
        item = response.meta['item']
        description = response.css(".description").xpath('.//text()').extract()
        description = ' '.join(description).strip()
        item['description'] = description

        slides = response.css(".img-thumbnail")
        images = slides.css('img').xpath('@src').extract()
        item['images'] = images

        tabs = [t.css("::text").get().strip()
                for t in response.css(".resp-tabs-list li")]
        resp_tabs = [r.css("::text").extract()
                     for r in response.css('.resp-tabs-container > .tab-content')]
        for tab, resp in zip(tabs, resp_tabs):
            if tab.lower() != 'size':
                continue
            _resp = '\n'.join([r.strip() for r in resp]).strip()
            item['measurements'] = _resp

        yield item
