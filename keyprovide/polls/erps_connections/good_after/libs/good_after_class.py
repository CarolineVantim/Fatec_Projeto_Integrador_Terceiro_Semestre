from polls.erps_connections.good_after.libs.references.headers import headers
from bs4 import BeautifulSoup
import requests

parameter = '5601286260024'

class SiteGoodAfter(object):
    """
        Class that connects into the online supermarket called
        GoodAfter and search for a specific product and return
        a json of the products
    """
    def __init__(self, term: str or None = None) -> None:
        self.term = term
        self.availiable = bool()
        self.all_occurrences = list()
        self.headers = headers
        self.all_links = list()
        self.second_soup = None
        if self.term:
            self.params = {
                'controller': 'search',
                's': self.term,
            }
        else:
            self.params = {
                'controller': 'search',
                's': 'food',
            }

    def send_search_requisition(self, term: str or None = None) -> None:
        if term:
            self.params['s'] = term
        self.response = requests.get(
            f'https://{self.headers["authority"]}/pt/pesquisa',
            params=self.params,
            headers=self.headers)
        if self.response.status_code not in range(200, 300):
            raise requests.exceptions.ConnectionError('Something went wrong!')
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
        self.box_products = self.soup.find_all('div', {'class': 'item ajax_block_product'})
        if len(self.box_products) > 0:
            for set_ in self.box_products:
                try:
                    self.all_links.append(set_.a['href'])
                    self.availiable = True
                except KeyError:
                    continue
        else:
            self.availiable = False

    def __clean_product_json(self) -> None:
        temp_dict = dict()
        wanted_keys = [
            'meta_keywords',
            'name',
            'description',
            'category',
            'attributes',
            'image',
            'reference',
            'price_tax_exc',
            'price_without_reduction'
        ]
        for key in wanted_keys:
            try:
                temp_dict[key] = self.product_dict[key]
            except KeyError:
                continue
        self.product_dict = temp_dict
        self.product_dict['product_link'] = self.product_link
        reference_date = self.product_dict
        reference_keys = ['attributes', '1', 'name']
        for key in reference_keys:
            reference_date = reference_date.get(key, '-')
            if reference_date == '-':
                break
        split_reference = reference_date.split(' - ') if reference_date != '-' else None
        self.product_dict['expired_date'] = split_reference[0] if split_reference else str()
        try:
            self.product_dict['price_from'] = self.product_dict.pop('price_without_reduction')
        except KeyError:
            self.product_dict['price_from'] = 0
        try:
            self.product_dict['price_to'] = self.product_dict.pop('price_tax_exc')
        except KeyError:
            self.product_dict['price_to'] = 0
        self.product_dict['marketplace'] = 'GoodAfter'

    def __extract_attributes_occurrence(self) -> dict():
        self.product_dict = dict()
        if self.second_soup:
            box_product = self.second_soup.find('div', {'class': 'tab-pane fade'})
            if box_product:
                box_product = box_product.get('data-product', None)
                if box_product:
                    box_product = box_product.replace('null', "''")
                    box_product = box_product.replace('false', "False")
                    box_product = box_product.replace('true', "True")
                    try:
                        self.product_dict = eval(box_product)
                        self.try_dict = self.product_dict
                    except NameError:
                        raise NameError('The dict transformation went wrong!')
                    if len(self.product_dict.keys()) > 0:
                        if self.product_dict not in self.all_occurrences:
                            self.image = self.second_soup.find('img', {'class': 'js-qv-product-cover'})
                            if self.image:
                                try:
                                    self.product_dict['image'] = self.image['src']
                                except KeyError:
                                    self.product_dict['image'] = str()
                            self.__clean_product_json()
                            self.all_occurrences.append(self.product_dict)

    def send_occurrence_requisition(self, product_link: str) -> None:
        self.second_soup = None
        self.product_link = str()
        if not 'https' in product_link:
            raise TypeError(f'The link {product_link} miss the connection protocol!')
        else:
            self.product_link = product_link
        self.second_response = requests.get(self.product_link, headers=self.headers)
        if self.second_response.status_code not in range(200, 300):
            raise requests.exceptions.ConnectionError('Something went wrong!')
        self.second_soup = BeautifulSoup(self.second_response.text, 'html.parser')
        self.__extract_attributes_occurrence()

    def extract_all_occurrences(self) -> None:
        for link in self.all_links:
            self.send_occurrence_requisition(link)
