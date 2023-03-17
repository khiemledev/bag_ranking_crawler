import scrapy
from ..items import BagRankingCrawlerItem



class ProductSpider(scrapy.Spider):
    name = "mightychic"
    start_urls = [
        "https://mightychic.com/collections/all-hermes-bags?view=infinite-scroll&page=1"]

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
                f"https://mightychic.com/collections/all-hermes-bags?view=infinite-scroll&page={int(response.url.split('=')[-1]) + 1}")
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def product_parse(self, response):
        item = response.meta['item']
        description = response.css(
            ".product__description").xpath('.//text()').extract()
        description = ' '.join(description).strip()
        item['description'] = description

        slides = response.css(".product__slideshow-slide")
        images = []
        for slide in slides:
            lmao = slide.xpath("@data-media-large-url").get()
            if lmao is not None and lmao is str:
                image = 'https:' + lmao 
                images.append(image)
        item['images'] = images
        yield item
