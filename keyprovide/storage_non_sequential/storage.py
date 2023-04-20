from pymongo import MongoClient


class MongoConnect:
	"""
		Class used to connect into a
		Mongo database
	"""
	def __init__(self) -> None:
		self.engine = MongoClient('localhost', 27017)
		self.db = self.engine.keyprovide
		self.colletion = self.db.keyprovide
		self.object_results = None
		self.results = list()
		self.count = None
		self.documents_count = int()

	def non_db_insert(self, elements: list[dict] or dict) -> None:
		if type(elements) is dict:
			self.report = self.colletion.insert_one(elements)
		elif type(elements) is list:
			self.report = self.colletion.insert_many(elements)

	def __extract_list_results(self) -> None:
		if self.object_results:
			key = self.results_log.get("executionStats", '-')
			self.count = key.get("nReturned", '-') if key != '-' else '-'
			try:
				self.count = int(self.count)
				self.results = [self.object_results.next() for _ in range(self.count)]
			except ValueError:
				self.results = list()

	def non_db_get(self, filters: dict) -> None:
		self.results_log = None
		self.object_results = self.colletion.find(filters)
		if self.object_results:
			self.results_log = self.object_results.explain()
			self.__extract_list_results()

	def non_db_delete(self, elements: list[dict] or dict) -> None:
		if type(elements) is dict:
			if len(elements.keys()) > 0:
				self.report = self.colletion.delete_one(elements)
		elif type(elements) is list:
			if len(elements) == 1:
				self.report = self.colletion.delete_many(elements[0])
			else:
				raise TypeError('Delete Error: Need to pass a list with only one dict condition')

	def count_documents(self, filters: dict = dict()) -> None:
		self.documents_count = self.colletion.count_documents(filters)

	def distinct_element(self, field: str) -> None:
		self.distinct_values = self.colletion.distinct(field)

# Documentation => https://www.mongodb.com/docs/v4.0/reference/command/clone/
