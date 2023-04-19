import json
import re

import scrapy

from ..items import BagRankingCrawlerItem


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
    name = "vestiairecollective"

    def start_requests(self):
        url = 'https://search.vestiairecollective.com/v1/product/search'
        headers = get_header()
        for f_sold in [False, True]:
            for i in range(101):
                body = create_body_req(i, f_sold)
                yield scrapy.Request(url=url, method='POST', headers=headers, body=json.dumps(body), callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body)
        items = data['items']
        for item in items:
            title = item['name']
            brand = item['brand']['name']
            desc = item['description']
            colors = ', '.join([clrs['name']
                               for clrs in item['colors']['all']]) if 'colors' in item else None
            link = "https://www.vestiairecollective.com/" + item['link']
            price = f"{item['price']['cents']} {item['price']['currency']}"
            is_sold = item['sold']
            model = item['model']['name'] if 'model' in item else None
            thumbnail = "https://images.vestiairecollective.com/cdn-cgi/image/w=3840,q=80,f=auto," + \
                item['pictures'][0]
            yield scrapy.Request(
                url=link,
                callback=self.parse_item,
                meta={
                    'item': BagRankingCrawlerItem(
                        title=title,
                        brand=brand,
                        description=desc,
                        color=colors,
                        link=link,
                        price=price,
                        is_sold=is_sold,
                        model=model,
                        thumbnail=thumbnail,
                    ),
                },
            )

    def parse_item(self, response):
        item = response.meta['item']

        price = response.xpath(
            '//*[@id="__next"]/div/main/div[1]/div[4]/div/div[1]/div/div[2]/div').css('::text').getall()
        price = ''.join(price).strip()
        sold_re = re.compile(r'Sold at\s*\$(.+)\son\s*(.+)')
        sold = sold_re.search(price)
        if sold is not None:
            item['sold_date'] = sold.group(2)

        images = response.css(
            'div[class^="p_productPage__top__image__k"]').css('img::attr(src)').getall()
        item['images'] = images

        li_list = response.xpath(
            '//*[@id="__next"]/div/main/section[1]/div/div/div[2]').css('li')
        desc = ''
        for li in li_list:
            desc += ''.join(li.css('::text').getall()) + '\n'

        condition_re = re.compile(r'Condition\s*:\s*(.+)')
        material_re = re.compile(r'Material\s*:\s*(.+)')

        if item['color'] is None:
            color_re = re.compile(r'Color\s*:\s*(.+)')
            color = color_re.search(desc)
            if color is not None:
                color = color.group(1)
            else:
                color = None

        if item['model'] is None:
            model_re = re.compile(r'Model\s*:\s*(.+)')
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

        item['material'] = material.strip() if material is not None else None
        item['condition'] = condition.strip(
        ) if condition is not None else None
        item['description'] = desc

        yield item
