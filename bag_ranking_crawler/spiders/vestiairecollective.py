import scrapy
import json
from ..items import BagRankingCrawlerItem
import re


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
            "x-usertoken": "anonymous-d08ba9dd-c8ae-4217-a003-2393905f4140",
            "x-correlation-id": "2c36a52c-3ba5-4b61-b9f7-457a92c11fab"
        }
        for check in [True, False]:
            for i in range(500):
                body = {
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
                        "sold": ["1"] if check else ['0']
                    },
                    "locale": {
                        "country": "US",
                        "currency": "USD",
                        "language": "us",
                        "sizeType": "US"
                    },
                }
                yield scrapy.Request(url=url, method='POST', headers=headers, body=json.dumps(body), callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body)
        items = data['items']
        for item in items:
            brand = item['brand']['name']
            yield scrapy.Request(url='https://www.vestiairecollective.com/'+item['link'], callback=self.parse_item, meta={'brand': brand})

    def parse_item(self, response):
        item = BagRankingCrawlerItem()
        item['title'] = response.css(
            '.product-main-heading_productTitle__name__x_rnE::text').get()
        price = response.xpath(
            '//*[@id="__next"]/div/main/div[1]/div[4]/div/div[1]/div/div[2]/div').css('::text').getall()
        price = ''.join(price).strip()
        sold_re = re.compile(r'Sold at\s*\$(.+)\son\s*(.+)')
        sold = sold_re.search(price)
        if sold is not None:
            item['price'] = sold.group(1)
            item['sold_date'] = sold.group(2)
        else:
            price_re = re.compile(r'\$(\d+,*\d+\.*\d+)')
            price = price_re.search(price)
            if price is not None:
                item['price'] = price.group(1)+'USD'
            else:
                item['price'] = None

        images = response.css(
            '.p_productPage__top__image__kNYZ4').css('img::attr(src)').getall()
        item['images'] = images
        item['link'] = response.url

        li_list = response.xpath(
            '//*[@id="__next"]/div/main/section[1]/div/div/div[2]').css('li')
        desc = ''
        for li in li_list:
            desc += ''.join(li.css('::text').getall()) + '\n'
        color_re = re.compile(r'Color\s*:\s*(.+)')
        model_re = re.compile(r'Model\s*:\s*(.+)')
        condition_re = re.compile(r'Condition\s*:\s*(.+)')
        material_re = re.compile(r'Material\s*:\s*(.+)')
        color = color_re.search(desc)
        if color is not None:
            color = color.group(1)
        else:
            color = None
        model = model_re.search(desc)
        if model is not None:
            model = model.group(1)
        else:
            model = None

        material = material_re.search(desc)
        if material is not None:
            material = material.group(1)
        else:
            material = None

        condition = condition_re.search(desc)
        if condition is not None:
            condition = condition.group(1)
        else:
            condition = None
        item['color'] = color.strip()
        item['model'] = model.strip()
        item['material'] = material.strip()
        item['condition'] = condition.strip()
        item['description'] = desc.strip()
        item['description'] = desc
        item['brand'] = response.meta['brand']
        yield item
