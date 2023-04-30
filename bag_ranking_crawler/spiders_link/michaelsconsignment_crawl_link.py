import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "michaelsconsignment_link"
    start_urls = [
        f"https://www.michaelsconsignment.com/collections/hermes/handbags?page={i}" for i in range(1, 2)]

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        links = response.css('a.product-link::attr(href)').getall()
        for link in links:
            item = BagCrawlLink()
            item['website_name'] = 'michaelsconsignment'
            item['link'] = 'https://www.michaelsconsignment.com' + link
            yield item
