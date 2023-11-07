
from django.db import models

class VerNum:
	v0:int=0
	v1:int=0
	v2:int=0
	v3:int=0
	db_val:int=0

	def __init__(self, val:str):
		'''
		val: 
			'0','0.0','0.0.0','0.0.0.0' <-> 0
			'123.456.789.012' <-> 123 456 789 012
			'0.2.3' <-> 2 003 000
			'0.0.3' <-> 3 000
			'0.0.0.111' <-> 111
			'1.2' <-> 1 002 000 000
			'1' <-> 1 000 000 000
		'''
		if val == '0' or val == '':
			return
		
		v0,v1,v2,v3 = self._str_to_ints(val)
		if v0 == v1 == v2 == v3 == 0: return
		self._init_from_ints((v0,v1,v2,v3))

	@classmethod
	def from_db_value(cls, value:int):
		vn = VerNum('0')
		if value <= 0:
			return vn
		vn.db_val = value
		vn.v3 = value % 1000
		v1k = int(value/1000)
		vn.v2 = v1k % 1000
		v1k = int(v1k/1000)
		vn.v1 = v1k % 1000
		vn.v0 = int(v1k/1000)
		return vn

	def _init_from_ints(self, v:tuple[int,int,int,int]):
		v0, v1, v2, v3 = v
		self.v0 = v0 if v0 < 1000 else 1000 * int(v0/1000)
		self.v1 = v1 if v1 < 1000 else 1000 * int(v1/1000)
		self.v2 = v2 if v2 < 1000 else 1000 * int(v2/1000)
		self.v3 = v3 if v3 < 1000 else 1000 * int(v3/1000)
		self.db_val = self.v0*1000*1000*1000
		self.db_val += self.v1*1000*1000
		self.db_val += self.v2*1000
		self.db_val += self.v3

	def _str_to_ints(self, value:str|None):
		v0 = v1 = v2 = v3 = 0
		if value is not None:
			vs = value.split('.')
			vs_len = len(vs)
			if vs_len > 0:
				try:
					if vs_len >= 1:
						v0 = int(vs[0])
					if vs_len >= 2:
						v1 = int(vs[1])
					if vs_len >= 3:
						v2 = int(vs[2])
					if vs_len >= 4:
						v3 = int(vs[3])
				except:
					pass
		return v0,v1,v2,v3

	def __str__(self) -> str:
		if self.v0 == self.v1 == self.v2 == self.v3 == 0:
			if self.db_val != 0:
				return f'{self.db_val}'
			return '0'
		v1s = f'.{self.v1}' if self.v1 > 0 else ''
		v2s = f'.{self.v2}' if self.v2 > 0 else ''
		v3s = f'.{self.v3}' if self.v3 > 0 else ''			
		return f'{self.v0}{v1s}{v2s}{v3s}'
	
	def __eq__(self, __value: object) -> bool:
		if not isinstance(__value, VerNum):
			__value = VerNum(str(__value))
		return self.db_val == __value.db_val

class FVer(models.Field):
	def __init__(self, *args, **kwargs):
		kwargs['default'] = 0
		super().__init__(*args, **kwargs)
	
	def db_type(self, connection):
		return 'bigint unsigned'

	def to_python(self, value):
		if isinstance(value, VerNum): return value
		vn = VerNum(str(value))
		return vn

	def from_db_value(self, value, expression, connection):
		return VerNum.from_db_value(value)

	def get_prep_value(self, value):
		if isinstance(value, VerNum): return value.db_val
		nv = VerNum(str(value))
		return nv.db_val
