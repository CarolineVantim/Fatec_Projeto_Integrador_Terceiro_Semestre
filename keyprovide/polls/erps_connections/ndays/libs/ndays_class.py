from polls.erps_connections.ndays.libs.references.headers import headers
from bs4 import BeautifulSoup
import datetime
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
        self.availiable = bool()
        self.possible_request_error = (requests.exceptions.ConnectTimeout,
                                        requests.exceptions.SSLError,
                                        requests.exceptions.ConnectionError,
                                        requests.exceptions.ReadTimeout)

    def __clean_product_json(self) -> None:
        today = datetime.datetime.now().date()
        self.product_dict['meta_keywords'] = self.product_dict.get('name')
        self.product_dict['description'] = self.product_dict.get('name')
        self.product_dict['price_from'] = self.product_dict['price_from'].replace('R$', '').replace(',', '.')
        self.product_dict['price_to'] = self.product_dict['price_to'].replace('R$', '').replace(',', '.')
        days_to_expire = int(self.product_dict['days_to_expire'])
        self.product_dict['expired_date'] = today + datetime.timedelta(days=days_to_expire)
        self.product_dict.pop('days_to_expire')
        box_reference = self.product_dict['image'].split('-')
        if len(box_reference) == 2:
            reference = box_reference[0].split('/')[-1]
            try:
                reference = int(reference)
            except ValueError:
                reference = str(f'{self.product_dict.get("name")}-{self.product_dict.get("expired_date")}')
        else:
            reference = str(f'{self.product_dict.get("name")}-{self.product_dict.get("expired_date")}')
        self.product_dict['reference'] = reference

    def __extract_attributes_occurrence(self, box_products: list) -> dict[str: str]:
        self.product_dict  = dict()
        for occurrence in box_products:
            days_to_expire = occurrence.find('p', {'class': 'txt2'})
            tag_image = occurrence.find('div', {'class': 'image'})
            product_link = occurrence('h4')
            if len(product_link) == 1:
                try:
                    product_link = product_link[0].a
                except AttributeError:
                    product_link = None
            if tag_image:
                try:
                    tag_image = tag_image.a.img
                except AttributeError:
                    tag_image = None
            price_from = occurrence.find('span', {'class': 'price-old'})
            price_to = occurrence.find('span', {'class': 'price-new'})
            self.product_dict = {
                'product_link': product_link.get('href', '-') if product_link else '-',
                'image': tag_image.get('src', '-') if tag_image else '-',
                'name': tag_image.get('title', '-') if tag_image else '-',
                'days_to_expire': days_to_expire.text if days_to_expire else '0',
                'price_from': price_from.text if price_from else '0',
                'price_to': price_to.text if price_to else '0',
                'marketplace': 'NDays',
                'category': 'NDays',
                'attributes': str()
            }
            self.__clean_product_json()
            self.all_occurrences.append(self.product_dict)

    def send_search_requisition(self, day_from: int or None = None, day_to: int or None = None) -> None:
        if day_from and day_to:
            self.params = {
            'due_date_begin': day_from,
            'due_date_end': day_to
        }
        try:
            self.response = requests.get(
                'https://www.ndays.com.br/index.php?route=product/seller',
                headers=self.headers,
                params=self.params)
        except self.possible_request_error:
            self.availiable = False
            return
        if self.response.status_code in range(200, 300):
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
            self.box_products = self.soup.find_all('div', {'class': 'product-thumb'})
            if len(self.box_products) > 0:
                self.__extract_attributes_occurrence(self.box_products)
                self.availiable = True
