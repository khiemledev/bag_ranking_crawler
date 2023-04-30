import scrapy

from bag_ranking_crawler.items import BagCrawlLink


class ProductSpider(scrapy.Spider):
    name = "luxcellent_link"
    start_urls = [
        f"https://luxcellent.com/collections/shop-all?page={i}" for i in range(1, 2)]
    # &filter.p.vendor=Hermès

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def parse(self, response):
        links = response.css('#product-grid a.full-unstyled-link::attr(href)').getall()
        for link in links:
            link = link.split("?")[0]
            link = 'https://luxcellent.com' + link
            item = BagCrawlLink()
            item['website_name'] = 'luxcellent'
            item['link'] = link
            yield item
