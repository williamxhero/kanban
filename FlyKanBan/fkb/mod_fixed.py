from typing import Any, TypeVar

from FlyKanBan.db_type.internal_fields import *

from fkb.mod_type import *


class User(models.Model):
	act = FChar32('账号', primary_key=True)
	nam = FChar32('姓名')
	nck = FChar32N('昵称')
	gdr = FChar32N('性别')
	grp = FChar32N('组别')

	class Meta():
		indexes = [
			Index('act'),
			Index('nam'),
			Index('nck'),
			Index('grp'),
		]

	@classmethod
	def make_pkeys(cls, act:Any, **kwargs)->dict[str,Any]|None:
		if act is None: return None
		return {'act':act}
	
	def __eq__(self, __value: object) -> bool:
		if isinstance(__value, dict):
			if 'act' in __value:
				return self.act == __value['act']

		return super().__eq__(__value)
	
	def __str__(self):
		return f'[U]{self.nam}({self.act})'
	
	def __hash__(self) -> int:
		return self.act.__hash__()



_T = TypeVar('_T', bound=str|None)

class Config(models.Model):
	key = FChar32('键', unique=True)
	val = models.TextField('值')

	@classmethod
	def get(cls, key:str, default:_T=None)->str|_T:
		dc = Config.objects.filter(key=key)
		if len(dc) == 0:
			return default
		kv = dc.get()
		return kv.val

	@classmethod
	def set(cls, key:str, value:str|None):
		dc = Config.objects.filter(key=key)
		if len(dc) == 0:
			if value is None:
				return
			Config(key=key, val=value).save()
			return
		
		if value is None:
			dc.delete()
			return
		
		kv = dc.get()
		kv.val = value
		kv.save()