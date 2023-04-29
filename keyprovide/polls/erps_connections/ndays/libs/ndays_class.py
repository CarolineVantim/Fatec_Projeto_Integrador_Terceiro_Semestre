from polls.erps_connections.ndays.libs.references.headers import headers
from bs4 import BeautifulSoup
import requests

'https://www.ndays.com.br/index.php?route=product/seller&due_date_begin=60&due_date_end=90'


class SiteNDays(object):
    """
        Class used to connect into the website
        and extract products occurrences based on
        the expiration date
    """
    def __init__(self, day_from: int or None = None, day_to: int or None = None) -> None:
        self.headers = headers
        self.params = {
            'due_date_begin': day_from if day_from else 1,
            'due_date_end': day_to if day_to else 30
        }
        self.all_occurrences = list()

    def __extract_attributes_occurrence(self, box_products: list) -> dict[str: str]:
        self.product_dict  = dict()
        for occurrence in box_products:
            days_to_expire = occurrence.find('p', {'class': 'txt2'})
            tag_image = occurrence.find('div', {'class': 'image'})
            if tag_image:
                try:
                    tag_image = tag_image.a.img
                except AttributeError:
                    tag_image = None
            price_from = occurrence.find('span', {'class': 'price-old'})
            price_to = occurrence.find('span', {'class': 'price-new'})
            self.product_dict = {
                'link': tag_image.get('src', '-') if tag_image else '-',
                'name': tag_image.get('title', '-') if tag_image else '-',
                'days_to_expire': days_to_expire.text if days_to_expire else '0',
                'price_from': price_from.text if price_from else '0',
                'price_to': price_to.text if price_to else '0'
            }
            self.all_occurrences.append(self.product_dict)

    def send_search_requisition(self, day_from: int or None = None, day_to: int or None = None) -> None:
        if day_from and day_to:
            self.params = {
            'due_date_begin': day_from,
            'due_date_end': day_to
        }
        self.response = requests.get(
            'https://www.ndays.com.br/index.php?route=product/seller',
            headers=self.headers,
            params=self.params)
        if self.response.status_code in range(200, 300):
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
            box_products = self.soup.find_all('div', {'class': 'product-thumb'})
            if len(box_products) > 0:
                self.__extract_attributes_occurrence(box_products)
