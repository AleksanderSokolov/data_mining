import os
import time
import json
from pathlib import Path
import requests

"""
GET
POST
PUT
PATCH
DELETE
"""

"""
1xx
2xx
3xx
4xx
5xx
"""


# headers = {
#     'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0"
# }
# params = {
#     'records_per_page': 50,
#     'page': 1,
# }
# url = 'https://5ka.ru/api/v2/special_offers/'
# response = requests.get(url, headers=headers)
#
# with open('5ka.html', 'w', encoding='UTF-8') as file:
#     file.write(response.text)

class StatusCodeError(Exception):
    def __init__(self, txt):
        self.txt = txt


class Parser5ka:
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    def __init__(self, start_url, category):
        self.category = category
        self.start_url = start_url

    def _get_response(self, url, **kwargs):
        while True:
            try:
                response = requests.get(url, **kwargs)
                if response.status_code != 200:
                    raise StatusCodeError(f'status {response.status_code}')
                return response
            except (requests.exceptions.ConnectTimeout,
                    StatusCodeError):
                time.sleep(0.1)

    def run(self):
        for products in self.parse(self.start_url):
            #for product in products:
            #    file_path = Path(__file__).parent.joinpath("json").joinpath(f'{product["id"]}.json')
            #    self.save_file(file_path, product)
            file_path = Path(__file__).parent.joinpath("json").joinpath(self.category +'.json')
            self.save_file(file_path, products)

    def parse(self, url):
        while url:
            response = self._get_response(url, headers=self.headers)
            data: dict = response.json()
            url = data['next']
            yield data.get('results', [])

    def parseCat(self, url):
        while url:
            response = self._get_response(url, headers=self.headers)
            data: dict = response.json()
            yield data

    def save_file(self, file_path: Path, data: dict):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='UTF-8') as file:
            # file.write(json.dumps(data))
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':

    parserCat = Parser5ka('https://5ka.ru/api/v2/categories/', '0')
    categories1 = parserCat.parseCat('https://5ka.ru/api/v2/categories/')

    for categories in categories1:
        for cat in categories:
            parser = Parser5ka('https://5ka.ru/api/v2/special_offers/?categories=' + cat.get('parent_group_code'), cat.get('parent_group_code'))
            # parser = Parser5ka('https://5ka.ru/api/v2/special_offers/')
            parser.run()