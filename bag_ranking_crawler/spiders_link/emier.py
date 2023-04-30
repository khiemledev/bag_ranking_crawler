import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "emier_link"
    start_urls = [
        f"https://emier.com.au/collections/hermes?page={i}" for i in range(245)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        # Extract product information
        # select all item has class collection__item
        products = response.css(".ProductItem")
        for product in products:
            link = product.css(
                "a.ProductItem__ImageWrapper").xpath("@href").get()
            item = BagCrawlLink()
            item['website_name'] = 'emier'
            item['link'] = 'https://emier.com.au' + link
            yield item
