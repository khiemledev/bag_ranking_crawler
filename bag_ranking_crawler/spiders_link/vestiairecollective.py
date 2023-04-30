import json

import scrapy

from bag_ranking_crawler.items import BagCrawlLink


def create_body_req(i, f_sold):
    return {
        "pagination": {
            "offset": i*48,
            "limit": 48
        },
        "fields": [
            "name",
            "description",
            "brand",
            "model",
            "country",
            "price",
            "discount",
            "link",
            "sold",
            "likes",
            "editorPicks",
            "shouldBeGone",
            "seller",
            "directShipping",
            "local",
            "pictures",
            "colors",
            "size",
            "stock",
            "universeId"
        ],
        "facets": {
            "fields": [
                "brand",
                "universe",
                "country",
                "stock",
                "color",
                "categoryLvl0",
                "priceRange",
                "price",
                "condition",
                "region",
                "editorPicks",
                "watchMechanism",
                "discount",
                "sold",
                "directShippingEligible",
                "directShippingCountries",
                "localCountries",
                "sellerBadge",
                "isOfficialStore",
                "materialLvl0",
                "size0",
                "size1",
                "size2",
                "size3",
                "size4",
                "size5",
                "size6",
                "size7",
                "size8",
                "size9",
                "size10",
                "size11",
                "size12",
                "size13",
                "size14",
                "size15",
                "size16",
                "size17",
                "size18",
                "size19",
                "size20",
                "size21",
                "size22",
                "size23",
                "model",
                "dealEligible"
            ],
            "stats": [
                "price"
            ]
        },
        "sortBy": "relevance",
        "filters": {
            "catalogLinksWithoutLanguage": [
                "/women-bags/",
            ],
            "brand.id": [
                "14", "50", "17"
            ],
            "sold": ["1"] if f_sold else ['0']
        },
        "locale": {
            "country": "US",
            "currency": "USD",
                        "language": "us",
                        "sizeType": "US"
        },
    }


def get_header():
    return {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "x-usertoken": "anonymous-d08ba9dd-c8ae-4217-a003-2393905f4140",
        "x-correlation-id": "2c36a52c-3ba5-4b61-b9f7-457a92c11fab"
    }

class ProductSpider(scrapy.Spider):
    name = "vestiairecollective_link"
    start_urls = []

    custom_settings = {
        "ITEM_PIPELINES": {
            "bag_ranking_crawler.pipelines.CrawlingLinkPipeline": 300,
        },
    }

    def start_requests(self):
        url = 'https://search.vestiairecollective.com/v1/product/search'
        headers = get_header()
        for f_sold in [False, True]:
            for i in range(101):
                body = create_body_req(i, f_sold)
                yield scrapy.Request(url=url, method='POST', headers=headers, body=json.dumps(body), callback=self.parse)


    def parse(self, response):
        data = json.loads(response.body)
        products = data['items']
        for product in products:
            item = BagCrawlLink()
            link = "https://www.vestiairecollective.com/" + product['link']
            item['website_name'] = 'vestiairecollective'
            item['link'] = link
            yield item
