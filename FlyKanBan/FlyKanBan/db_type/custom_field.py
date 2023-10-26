from abc import abstractmethod

from django.db import models

class CustomValue:
	def __init__(self, value:str):
		...

	@abstractmethod
	def db_value(self)->str:
		...

	def __str__(self) -> str:
		return self.db_value()


class CustomField(models.Field):

	max_length = 32
	data_type:type[CustomValue] = CustomValue
	col_type = 'varchar'

	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = self.max_length
		super().__init__(*args, **kwargs)

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		return name, path, args, kwargs
	
	def db_type(self, connection):
		return f'{self.col_type}({self.max_length})'

	def to_python(self, value):
		if isinstance(value, self.data_type): return value
		return self.data_type(value)

	def from_db_value(self, value, expression, connection):
		return self.to_python(value)

	def get_prep_value(self, value):
		pyv = self.to_python(value)
		return pyv.db_value()
		
