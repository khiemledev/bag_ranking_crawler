import json

import scrapy

from ..items import BagRankingCrawlerItem


class ProductSpider(scrapy.Spider):
    name = "ginzaxiaoma"

    def start_requests(self):
        url = 'https://ginzaxiaoma.com/mall-portal/search/esProduct/search'
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "x-algolia-api-key": "ODgwMGVmNTZlODg5OWFjODE1ZDg5NzJiZDc0ZTQ5MzRjYmIzNjMxNGU4ODdlOGMxNzc5ZjBjZDAxODVjYmI4YnZhbGlkVW50aWw9MTY3OTEzODAxNiZyZXN0cmljdEluZGljZXM9YXR0cmlidXRlX2ZpeGVkX3ZhbHVlcyUyQ3Byb2RfYXR0cmlidXRlX2ZpeGVkX3ZhbHVlcyUyQ3Byb2RfYXR0cmlidXRlX2ZpeGVkX3ZhbHVlc18qJTJDYXVjdGlvbnMlMkNwcm9kX2F1Y3Rpb25zJTJDcHJvZF9hdWN0aW9uc18qJTJDcHJvZF9hdWN0aW9uc19uYW1lX2FzYyUyQ3Byb2RfYXVjdGlvbnNfbmFtZV9kZXNjJTJDcHJvZF9hdWN0aW9uc19zdGFydERhdGVfYXNjJTJDcHJvZF9hdWN0aW9uc19zdGFydERhdGVfZGVzYyUyQ3Byb2RfYXVjdGlvbnNfZW5kRGF0ZV9hc2MlMkNwcm9kX2F1Y3Rpb25zX2VuZERhdGVfZGVzYyUyQ3Byb2RfYXVjdGlvbnNfY2xvc2VEYXRlX2FzYyUyQ3Byb2RfYXVjdGlvbnNfY2xvc2VEYXRlX2Rlc2MlMkNjcmVhdG9ycyUyQ3Byb2RfY3JlYXRvcnMlMkNwcm9kX2NyZWF0b3JzXyolMkNjcmVhdG9yc1YyJTJDcHJvZF9jcmVhdG9yc1YyJTJDcHJvZF9jcmVhdG9yc1YyXyolMkNpdGVtcyUyQ3Byb2RfaXRlbXMlMkNwcm9kX2l0ZW1zXyolMkNsb3RzJTJDcHJvZF9sb3RzJTJDcHJvZF9sb3RzXyolMkNwcm9kX2xvdHNfbG90TnJfYXNjJTJDcHJvZF9sb3RzX2xvdE5yX2Rlc2MlMkNwcm9kX2xvdHNfYXVjdGlvbkRhdGVfYXNjJTJDcHJvZF9sb3RzX2F1Y3Rpb25EYXRlX2Rlc2MlMkNwcm9kX3VwY29taW5nX2xvdHNfYXNjJTJDcHJvZF91cGNvbWluZ19sb3RzX2Rlc2MlMkNwcm9kX2xvdHNfbG93RXN0aW1hdGVfYXNjJTJDcHJvZF9sb3RzX2xvd0VzdGltYXRlX2Rlc2MlMkNwcm9kX3N1Z2dlc3RlZF9sb3RzJTJDcHJvZF9meWVvX2xvdHNfYXVjdGlvbkRhdGVfYXNjJTJDcHJvZF9meWVvX2xvdHNfYXVjdGlvbkRhdGVfZGVzYyUyQ29iamVjdF90eXBlcyUyQ3Byb2Rfb2JqZWN0X3R5cGVzJTJDcHJvZF9vYmplY3RfdHlwZXNfKiUyQ2F0dHJpYnV0ZXMlMkNwcm9kX2F0dHJpYnV0ZXMlMkNwcm9kX2F0dHJpYnV0ZXNfKiUyQ3BpZWNlcyUyQ3Byb2RfcGllY2VzJTJDcHJvZF9waWVjZXNfKiUyQ3Byb2R1Y3RfaXRlbXMlMkNwcm9kX3Byb2R1Y3RfaXRlbXMlMkNwcm9kX3Byb2R1Y3RfaXRlbXNfKiUyQ3Byb2RfcHJvZHVjdF9pdGVtc19sb3dFc3RpbWF0ZV9hc2MlMkNwcm9kX3Byb2R1Y3RfaXRlbXNfbG93RXN0aW1hdGVfZGVzYyUyQ3Byb2RfcHJvZHVjdF9pdGVtc19wdWJsaXNoRGF0ZV9hc2MlMkNwcm9kX3Byb2R1Y3RfaXRlbXNfcHVibGlzaERhdGVfZGVzYyUyQ3NvdGhlYnlzX2NhdGVnb3JpZXMlMkNzb3RoZWJ5c19jYXRlZ29yaWVzJTJDc290aGVieXNfY2F0ZWdvcmllc18qJTJDdGFnZ2luZ190YWdzZXRzJTJDcHJvZF90YWdnaW5nX3RhZ3NldHMlMkNwcm9kX3RhZ2dpbmdfdGFnc2V0c18qJTJDdGFnZ2luZ190YWdzJTJDcHJvZF90YWdnaW5nX3RhZ3MlMkNwcm9kX3RhZ2dpbmdfdGFnc18qJTJDb25ib2FyZGluZ190b3BpY3MlMkNwcm9kX29uYm9hcmRpbmdfdG9waWNzJTJDcHJvZF9vbmJvYXJkaW5nX3RvcGljc18qJTJDZm9sbG93YWJsZV90b3BpY3MlMkNwcm9kX2ZvbGxvd2FibGVfdG9waWNzJTJDcHJvZF9mb2xsb3dhYmxlX3RvcGljc18qJTJDd2luZSUyQ3Byb2Rfd2luZSUyQ3Byb2Rfd2luZV8qJmZpbHRlcnM9Tk9UK3N0YXRlJTNBQ3JlYXRlZCtBTkQrTk9UK3N0YXRlJTNBRHJhZnQrQU5EK05PVCtpc1Rlc3RSZWNvcmQlM0QxK0FORCslMjhOT1QrbG9jYXRpb24lM0ElMjJTaGFuZ2hhaStBdWN0aW9uJTIyJTI5K0FORCtOT1QrbG90U3RhdGUlM0FDcmVhdGVkK0FORCtOT1QrbG90U3RhdGUlM0FEcmFmdCtBTkQrJTI4Tk9UK2lzSGlkZGVuJTNBdHJ1ZStPUitsZWFkZXJJZCUzQTAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMCUyOQ",
            "x-algolia-application-id": "KAR1UEUPJD"
        }
        for page in range(1, 28):
            body = {
                "productAttrs": [],
                "productCategoryId": "53",
                "productCategoryIds": "",
                "sort": 1,
                "page": page,
                "size": 18,
            }
            yield scrapy.Request(url=url, method='POST', headers=headers, body=json.dumps(body), callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body)
        items = data['data']['list']
        for e in items:
            item = BagRankingCrawlerItem(
                title=e['detailTitle'],
                thumbnail=e['pic'],
                link='https://ginzaxiaoma.com/product/'+str(e['id'])
            )
            yield scrapy.Request(url='https://ginzaxiaoma.com/mall-portal/pms/product/'+str(e['id']), callback=self.product_parse, meta={'item': item})

    def product_parse(self, response):
        item = response.meta['item']

        data = json.loads(response.body)
        data = data['data']
        images = data['albumPics'].split(',')
        item['images'] = images
        item['price'] = str(data['price']) + ' ' + data['currency']
        item['brand'] = data['brandName']
        item['model'] = data['attrModel']
        item['color'] = data['attrColors']
        item['material'] = data['attrMaterial']
        item['hardware'] = data['attrHardware']
        item['measurements'] = data['attrSize']
        item['condition'] = data['rank']
        yield item
