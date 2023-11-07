from typing import Any
from django.db import models

## CUSTOM FIELDS:

class Index(models.Index):
	def __init__(self, *args:Any, **kwargs:Any):
		if args:
			if 'fields' not in kwargs:
				kwargs['fields'] = args
			if 'name' not in kwargs:
				kwargs['name'] = f'idx_{"_".join(args)}'
			super().__init__(**kwargs)
		else:
			super().__init__(*args, **kwargs)

def nullable(super:Any, *args:Any, **kwargs:Any):
	kwargs['null'] = True
	kwargs['blank'] = True
	super.__init__(*args, **kwargs)

def notnull(super:Any, *args:Any, **kwargs:Any):
	kwargs['null'] = False
	kwargs['blank'] = False
	super.__init__(*args, **kwargs)


class FUInt(models.PositiveIntegerField):
	''' F: Field '''
	def __init__(self, *args:Any, **kwargs:Any):
		kwargs['default'] = 0
		super().__init__(*args, **kwargs)

class FUIntN(models.PositiveIntegerField):
	''' 
	F: Field
	N: Nullable
	'''
	def __init__(self, *args:Any, **kwargs:Any):
		nullable(super(), *args, **kwargs)

class FChar32(models.CharField):
	''' F: Field '''
	def __init__(self, *args:Any, **kwargs:Any):
		kwargs['max_length']=32
		super().__init__(*args, **kwargs) 

class FChar32N(FChar32):
	'''
	F: Field
	N: Nullable
	'''
	def __init__(self, *args:Any, **kwargs:Any):
		nullable(super(), *args, **kwargs)

class FTextN(models.TextField):
	'''
	F: Field
	N: Nullable
	'''
	def __init__(self, *args:Any, **kwargs:Any):
		nullable(super(), *args, **kwargs)

class FFloatN(models.FloatField):
	'''
	F: Field
	N: Nullable
	'''
	def __init__(self, *args:Any, **kwargs:Any):
		nullable(super(), *args, **kwargs)

class FDateTimeN(models.DateTimeField):
	'''
	F: Field
	N: Nullable
	'''
	def __init__(self, *args:Any, **kwargs:Any):
		nullable(super(), *args, **kwargs)

class FDurationN(models.DurationField):
	'''
	F: Field
	N: Nullable
	'''
	def __init__(self, *args:Any, **kwargs:Any):
		nullable(super(), *args, **kwargs)

class KND(models.ForeignKey):
	''' 
	K: Foreign Key
	N: Nullable
	D: DO_NOTHING
	'''
	def __init__(self, to:type[Any]|str, verbose_name:str, related_name:str, 
			  **kwargs:Any):
		kwargs['to'] = to
		kwargs['verbose_name'] = verbose_name
		kwargs['related_name'] = related_name
		kwargs['on_delete'] = models.DO_NOTHING
		nullable(super(), **kwargs)

class KC(models.ForeignKey):
	''' 
	K: Foreign Key
	C: CASCADE
	'''
	def __init__(self, to:type[Any]|str, verbose_name:str, related_name:str, 
			  **kwargs:Any):
		kwargs['to'] = to
		kwargs['verbose_name'] = verbose_name
		kwargs['related_name'] = related_name
		kwargs['on_delete'] = models.CASCADE
		super().__init__(**kwargs)

class FStt(models.CharField):
	'''
	F: Field  Status
	'''
	def __init__(self, verbose_name:str, choices:list[tuple[str,str]], default:str, 
			  **kwargs:Any):
		kwargs['max_length']=3
		kwargs['verbose_name'] = verbose_name
		kwargs['choices']= choices
		kwargs['default'] = default
		super().__init__(**kwargs)

class FSttN(models.CharField):
	'''
	F: Field  Status
	N: Nullable
	'''
	def __init__(self, verbose_name:str, choices:list[tuple[str,str]],
			  **kwargs:Any):
		kwargs['max_length']=3
		kwargs['verbose_name'] = verbose_name
		kwargs['choices']= choices
		nullable(super(), **kwargs)

class KUserND(models.ForeignKey):
	''' 
	K: Foreign Key
	N: Nullable
	D: DO_NOTHING
	'''
	def __init__(self, verbose_name:str, related_name:str, *arg:Any, **kwargs:Any):
		kwargs['verbose_name'] = verbose_name
		kwargs['related_name'] = related_name
		kwargs['to'] = 'User'
		kwargs['on_delete'] = models.DO_NOTHING
		nullable(super(), *arg, **kwargs) 


class F1To1CN(models.OneToOneField):
	'''
	F: Field 1 To 1
	C: Cascade
	N: Nullable
	'''
	def __init__(self, to:type[Any]|str, **kwargs:Any):
		kwargs['to'] = to
		#kwargs['related_name'] = related_name
		kwargs['on_delete'] = models.CASCADE
		nullable(super(), **kwargs)


class F1To1C(models.OneToOneField):
	'''
	F: Field 1 To 1
	C: Cascade
	N: Nullable
	'''
	def __init__(self, to:type[Any]|str, **kwargs:Any):
		kwargs['to'] = to
		#kwargs['related_name'] = related_name
		kwargs['on_delete'] = models.CASCADE
		super().__init__(**kwargs)

class FNToNN(models.ManyToManyField):
	'''
	F: Field N to N
	N: Nullable
	'''
	def __init__(self, to:type[Any]|str, through:type[Any]|str='', **kwargs:Any):
		kwargs['to'] = to
		kwargs['blank'] = True
		if through != '':
			kwargs['through'] = through
		super().__init__(**kwargs)