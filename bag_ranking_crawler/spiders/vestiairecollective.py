import scrapy
import json
from ..items import BagRankingCrawlerItem



class ProductSpider(scrapy.Spider):
    name = "vestiairecollective"

    def start_requests(self):
        url = 'https://search.vestiairecollective.com/v1/product/search'
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
        }
        for i in range(50):
            body = {
                "pagination": {
                    "offset": i * 200,
                    "limit": 200
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
                "q": None,
                "sortBy": "relevance",
                "filters": {
                    "catalogLinksWithoutLanguage": [
                        "/hermes/"
                    ],
                    "brand.id": [
                        "14"
                    ]
                },
                "locale": {
                    "country": "VN",
                    "currency": "USD",
                    "language": "us",
                    "sizeType": "US"
                },
                "mySizes": None
            }
            yield scrapy.Request(url=url, method='POST', headers=headers, body=json.dumps(body), callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body)
        items = data['items']
        for item in items:
            item = BagRankingCrawlerItem(
                title=item['name'],
                price=item['price']['cents'],
                link='https://www.vestiairecollective.com' + item['link'],
                thumbnail='https://images.vestiairecollective.com'+item['pictures'][0],
                description=item['description'],
            )
            yield item
