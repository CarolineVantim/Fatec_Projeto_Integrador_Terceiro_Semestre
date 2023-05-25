from polls.erps_connections.openai.connection_class import GenerateAttributesText
from polls.erps_connections.good_after.libs.good_after_class import SiteGoodAfter
from polls.erps_connections.ndays.libs.ndays_class import SiteNDays
from django.test import TestCase
import pathlib
import openai

class HomeTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/home')

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_text(self):
        self.assertContains(self.response, 'Entrar')

    def test_templates_home(self):
        self.assertTemplateUsed(self.response, 'home.html')


class LoginTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/login_user')

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_text(self):
        self.assertContains(self.response, 'Entrar')

    def test_templates_home(self):
        self.assertTemplateUsed(self.response, 'login_user.html')


class LogoutTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/logout_user')

    def test_302_response(self):
        self.assertEqual(self.response.status_code, 302)

    def test_templates_home(self):
        self.assertTemplateNotUsed(self.response)


class ResgistrationTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/register')

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_text(self):
        self.assertContains(self.response, 'Cadastrar')

    def test_templates_home(self):
        self.assertTemplateUsed(self.response, 'registration.html')


class APIGoodAfterTest(TestCase):
    def setUp(self):
        self.product_link = 'https://goodafter.com/pt/mercearia/13220-35418-oleo-virgem-coco-bio-200ml.html#/25616-consumo_preferencial-2023_04_08_202305181740_3580281930045'
        self.search_goodafter = SiteGoodAfter('food')
        self.search_goodafter.send_search_requisition()
        self.wanted_keys = [
            'meta_keywords',
            'name',
            'description',
            'category',
            'attributes',
            'image',
            'reference',
            'product_link',
            'expired_date',
            'price_from',
            'price_to',
            'marketplace'
        ]

    def test_attribute_types(self):
        self.assertIs(type(self.search_goodafter.headers), dict)
        self.assertIs(type(self.search_goodafter.term), str)
        self.assertIs(type(self.search_goodafter.availiable), bool)
        self.assertIs(type(self.search_goodafter.all_links), list)
        self.assertIs(type(self.search_goodafter.all_links[0]), str)

    def test_status_code(self):
        self.assertIn(self.search_goodafter.response.status_code, range(200, 300))

    def test_is_connected(self):
        self.assertTrue(self.search_goodafter.availiable)

    def test_https_protocol(self):
        count_https = 0
        for link in self.search_goodafter.all_links:
            if 'https' in link:
                count_https += 1    
        self.assertEquals(count_https, len(self.search_goodafter.all_links))

    def test_has_occurrences(self):
        self.search_goodafter.extract_all_occurrences()
        self.test_is_connected()
        self.assertGreater(len(self.search_goodafter.all_occurrences), 0)
    
    def test_verifing_occurrences(self):
        self.test_has_occurrences()
        self.assertIs(type(self.search_goodafter.all_occurrences[0]), dict)
        self.assertGreater(len(self.search_goodafter.all_occurrences[0].keys()), 0)
        self.assertIsNot(self.search_goodafter.all_occurrences[0].get('image', '-'), '-')

    def test_checking_output_json_keys_count(self):
        self.test_has_occurrences()
        count = 0
        for key in self.wanted_keys:
            if key in self.search_goodafter.all_occurrences[0].keys():
                count += 1
        self.assertEqual(len(self.wanted_keys), count)

    def test_checking_output_json_keys_names(self):
        self.test_has_occurrences()
        all_json_keys = list(self.search_goodafter.all_occurrences[0].keys())
        self.assertEqual(set(all_json_keys), set(self.wanted_keys))

    def test_raising_error(self):
        with self.assertRaises(TypeError):
            self.search_goodafter.send_occurrence_requisition(self.product_link.replace('https://', str()))

    def test_second_connection(self):
        self.search_goodafter.send_occurrence_requisition(self.product_link)
        self.assertIn(self.search_goodafter.second_response.status_code, range(200, 300))

    def test_occurrence_second_soup(self):
        self.test_second_connection()
        self.assertIsNotNone(self.search_goodafter.second_soup)


class APINDaysTest(TestCase):
    def setUp(self):
        self.search_ndays = SiteNDays()
        self.search_ndays.send_search_requisition()
        self.wanted_keys = [
            'meta_keywords',
            'name',
            'description',
            'category',
            'attributes',
            'image',
            'reference',
            'product_link',
            'expired_date',
            'price_from',
            'price_to',
            'marketplace'
        ]

    def test_attribute_types(self) -> None:
        self.assertIs(type(self.search_ndays.headers), dict)
        self.assertIs(type(self.search_ndays.params), dict)

    def test_status_code(self) -> None:
        self.assertIn(self.search_ndays.response.status_code, range(200, 300))

    def test_is_connected(self) -> None:
        self.assertTrue(self.search_ndays.availiable)

    def test_https_protocol(self) -> None:
        products_links = [occurrence.get('product_link') for occurrence in self.search_ndays.all_occurrences]
        count_https = int()
        for link in products_links:
            if 'https' in link:
                count_https += 1    
        self.assertEquals(count_https, len(self.search_ndays.all_occurrences))

    def test_has_occurrences(self) -> None:
        self.assertGreater(len(self.search_ndays.all_occurrences), 0)

    def test_verifing_occurrences(self) -> None:
        self.assertIs(type(self.search_ndays.all_occurrences[0]), dict)
        self.assertGreater(len(self.search_ndays.all_occurrences[0].keys()), 0)
        self.assertIsNot(self.search_ndays.all_occurrences[0].get('image', '-'), '-')

    def test_checking_output_json_keys_count(self) -> None:
        self.test_has_occurrences()
        count = 0
        for key in self.wanted_keys:
            if key in self.search_ndays.all_occurrences[0].keys():
                count += 1
        self.assertEqual(len(self.wanted_keys), count)

    def test_checking_output_json_keys_names(self) -> None:
        self.test_has_occurrences()
        all_json_keys = list(self.search_ndays.all_occurrences[0].keys())
        self.assertEqual(set(all_json_keys), set(self.wanted_keys))

    def test_occurrence_soup(self) -> None:
        self.assertIsNotNone(self.search_ndays.soup)

class APIOpenAITest(TestCase):
    def setUp(self) -> None:
        self.openai = GenerateAttributesText(False)
        self.openai.extract_specific_data('product', 'Desodorante Nívea masculino 50ml')
        self.wanted_keys = ['id', 'object', 'created', 'model', 'choices', 'usage']

    def test_attribute_types(self) -> None:
        self.assertIs(type(self.openai.availiable), bool)
        self.assertIs(type(self.openai.saving), bool)
        self.assertIs(type(self.openai.destination), pathlib.WindowsPath)
        self.assertIs(type(self.openai.statement), str)

    def test_response_object(self) -> None:
        self.assertIs(type(self.openai.response), openai.openai_object.OpenAIObject)

    def test_is_connected(self) -> None:
        self.assertTrue(self.openai.availiable)

    def test_has_occurrences(self) -> None:
        self.assertGreater(len(self.openai.results), 0)

    def test_verifing_occurrences(self) -> None:
        self.assertIs(type(self.openai.response.get('choices')), list)
        self.assertIs(type(self.openai.response.get('id')), str)
        self.assertIs(type(self.openai.response.get('usage')), openai.openai_object.OpenAIObject)

    def test_checking_output_json_keys_count(self) -> None:
        temp_list = list()
        all_response_keys = list(self.openai.response.keys())
        for key in self.openai.response.keys():
            temp_list.append(key in all_response_keys)
        self.assertEqual(temp_list.count(True), len(self.wanted_keys))

    def test_checking_output_json_keys_names(self) -> None:
        self.test_has_occurrences()
        all_json_keys = list(self.openai.response.keys())
        self.assertEqual(set(all_json_keys), set(self.wanted_keys))

    def test_has_right_statement(self) -> None:
        product = 'Desodorante Nívea masculino'
        self.assertIn('Escreva uma descrição', self.openai.statement)
        self.assertIn(product.lower(), self.openai.results.lower())

    def test_right_models(self) -> None:
        self.assertEqual(self.openai.response.get('model'), 'text-davinci-003')
        self.assertEqual(self.openai.response.get('object'), 'text_completion')

    def test_occurrence_second_soup(self) -> None:
        self.test_verifing_occurrences()
        text_response = self.openai.response.get('choices')
        self.assertIsNotNone(text_response)
