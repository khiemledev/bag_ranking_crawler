import scrapy


class Item(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    thumbnail = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()


class ProductSpider(scrapy.Spider):
    name = "vestiairecollective"
    start_urls = [
        "https://www.vestiairecollective.com/hermes/p-{}/#brand=Herm%C3%A8s%2314".format(i) for i in range(1, 2)]

    def parse(self, response):
        # Extract product information
        products = response.css(".product-card_productCard__2JCqK")
        print(products)
        for product in products:
            title = product.css("span").xpath(".//a/text()").get()
            link = product.css(
                ".product-card_productCard__productDetails__KIQmB").xpath(".//a/@href").get()
            price = product.xpath(
                ".//span[@class='product-card_productCard__text--price___l1Dn']/text()").get()
            thumbnail = 'https:' + \
                product.css(
                    '.vc-images_imageContainer__Sau2S').xpath("@src").get()
            item = Item()
            item['title'] = title
            item['price'] = price
            item['link'] = link
            item['thumbnail'] = thumbnail
            yield item
            # yield response.follow(url=link, callback=self.product_parse, meta={'item': item})

    # def product_parse(self, response):
    #     item = response.meta['item']
    #     description = response.css(
    #         ".product__description").xpath('.//text()').extract()
    #     description = ' '.join(description).strip()
    #     item['description'] = description

    #     slides = response.css(".product__slideshow-slide")
    #     images = []
    #     for slide in slides:
    #         image = 'https:' + slide.xpath("@data-media-large-url").get()
    #         images.append(image)
    #     item['images'] = images
    #     yield item
