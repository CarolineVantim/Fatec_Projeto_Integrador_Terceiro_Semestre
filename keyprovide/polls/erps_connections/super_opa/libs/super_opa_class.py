import requests



params = {
    'termo': 'asd',
}

response = requests.get('https://superopa.com/busca/produto/global', params=params, cookies=cookies, headers=headers)