# from libs.data_manipulation import save_occurrence_information
# from libs.data_manipulation import manipulating_data
# from libs.data_manipulation import verify_path_file
from polls.erps_connections.openai.statement.statement import statement
from pathlib import Path
import openai
import json
import os


class GenerateAttributesText:
    """
        Class used to connect into the openai API
        and pass a statement to the IA
        and treat the output data
    """
    def __init__(self, saving: bool = True):
        self.session_openai = openai
        self.statement = statement['first']
        self.my_path = os.getcwd()
        self.my_path = self.my_path.replace('\\', '/')
        self.saving = saving
        self.destination = Path(f'{self.my_path}/polls/erps_connections/openai/credentials/credentials.json')
        if self.destination.is_file():
            self.auth = open(self.destination)
            self.auth = self.auth.read()
            self.auth = json.loads(self.auth)
        else:
            raise ValueError("The credentials JSON isn't on the libs PATH")
        self.session_openai.api_key = self.auth.get('credentials', '-').get('key', '-')
        if self.session_openai.api_key == '-':
            raise ValueError("The auth key isn't on the credentials JSON")
        self.response = None
        self.availiable = True
        self.results = str()

    def send_requisition(self) -> None:
        if self.statement == '':
            raise ValueError('The statement is empty!')
        self.response = self.session_openai.Completion.create(
            model="text-davinci-003",
            prompt = self.statement,
            temperature=0.5,
            max_tokens=3500,
        )
        if self.response.choices[0]['finish_reason'] != 'stop':
            self.reason = self.response.choices[0]['finish_reason']
            self.availiable = False
        else:
            self.results = self.response.choices[0]['text'].strip()

    def extract_json(self) -> None:
        if self.response:
            try:
                self.results = eval(self.response.choices[0]['text'].strip())
            except SyntaxError:
                self.results = self.response.choices[0]['text']

    def load_train_data(self):
        first_set = manipulating_data()
        second_set = manipulating_data()
        self.data_set = dict()
        for element in first_set + second_set:
            if element[0].lower() == 'null' or element[1].lower() == 'null':
                continue
            try:
                self.data_set[element[0]].append(element[1])
            except KeyError:
                self.data_set[element[0]] = list()
                self.data_set[element[0]].append(element[1])

    def load_wanted_data(self):
        self.wanted_date = manipulating_data()
        self.wanted_date = self.wanted_date[1:1]
        self.statement = f'{statement["fourth"]}\nlista1 = {self.wanted_date}'
        self.statement = statement['third']

    def extract_specific_data(self, parameter: str, name: str):
        self.statement = f'{statement["first"]}{name}'
        self.send_requisition()
        if self.availiable and self.saving:
            save_occurrence_information({'id': parameter, 'description': self.results}, 'output_description_product')
