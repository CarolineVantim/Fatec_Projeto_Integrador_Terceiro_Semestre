from polls.good_after.libs.good_after_class import SiteGoodAfter
from django.test import TestCase


class HomeTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/polls/home')

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_text(self):
        self.assertContains(self.response, 'Entrar')

    def test_templates_home(self):
        self.assertTemplateUsed(self.response, 'home.html')


class LoginTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/polls/login_user')

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_text(self):
        self.assertContains(self.response, 'Entrar')

    def test_templates_home(self):
        self.assertTemplateUsed(self.response, 'login_user.html')


class LogoutTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/polls/logout_user')

    def test_302_response(self):
        self.assertEqual(self.response.status_code, 302)

    def test_templates_home(self):
        self.assertTemplateNotUsed(self.response)


class ResgistrationTest(TestCase):
    def setUp(self):
        self.response = self.client.get('/polls/register')

    def test_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_text(self):
        self.assertContains(self.response, 'Cadastrar')

    def test_templates_home(self):
        self.assertTemplateUsed(self.response, 'registration.html')


class APIGoodAfterTest(TestCase):
    def setUp(self):
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
            'expired_date'
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
        product_link = 'https://goodafter.com/pt/mercearia/13049-34868-churruca-picadita-mix-frutos-secos-1kg.html'
        with self.assertRaises(TypeError):
            self.search_goodafter.send_occurrence_requisition(product_link.replace('https://', str()))

    def test_second_connection(self):
        product_link = 'https://goodafter.com/pt/mercearia/13049-34868-churruca-picadita-mix-frutos-secos-1kg.html'
        self.search_goodafter.send_occurrence_requisition(product_link)
        self.assertIn(self.search_goodafter.second_response.status_code, range(200, 300))

    def test_occurrence_second_soup(self):
        self.test_second_connection()
        self.assertIsNotNone(self.search_goodafter.second_soup)
