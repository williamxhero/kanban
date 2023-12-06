from typing import Any
from django.db import models

## CUSTOM FIELDS:

class Index(models.Index):
	def __init__(self, *args:Any, **kwargs:Any):
		if args:
			fields = args
		elif 'fields' in kwargs:
			fields = kwargs['fields']
		else:
			raise Exception('Index need fields')
		
		kwargs['fields'] = fields
		fields = "_".join(fields)

		name = ''
		if 'add' in kwargs:
			add = kwargs['add']
			name = f'_{add}'
			del kwargs['add']

		kwargs['name'] = f'idx_{fields}{name}'
		super().__init__(**kwargs)

def nullable(super:Any, *args:Any, **kwargs:Any):
	kwargs['null'] = True
	kwargs['blank'] = True
	super.__init__(*args, **kwargs)

def notnull(super:Any, *args:Any, **kwargs:Any):
	kwargs['null'] = False
	kwargs['blank'] = False
	super.__init__(*args, **kwargs)

class FUBigInt(models.PositiveBigIntegerField):
	''' F: Field
	U: unsigned
	'''
	def __init__(self, *args:Any, **kwargs:Any):
		kwargs['default'] = 0
		super().__init__(*args, **kwargs)

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

class KD(models.ForeignKey):
	''' 
	K: Foreign Key
	D: DO_NOTHING
	'''
	def __init__(self, to:type[Any]|str, verbose_name:str, related_name:str, 
			  **kwargs:Any):
		kwargs['to'] = to
		kwargs['verbose_name'] = verbose_name
		kwargs['related_name'] = related_name
		kwargs['on_delete'] = models.DO_NOTHING
		super().__init__(**kwargs)

class KC(models.ForeignKey):
	''' 
	K: Foreign Key
	C: CASCADE 一并删除子
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
	def __init__(self, verbose_name:str, *arg:Any, **kwargs:Any):
		if 'add' in kwargs:
			add = '_' + kwargs['add'] 
			del kwargs['add']
		else:
			add = ''
		kwargs['verbose_name'] = verbose_name
		kwargs['related_name'] = KUserND._name2col(verbose_name, add)
		kwargs['to'] = 'User'
		kwargs['on_delete'] = models.DO_NOTHING
		nullable(super(), *arg, **kwargs) 

	NAMES = {
		'创建':'crt',
		'关闭':'cls',
		'负责':'rsp',
		'评审':'rev',
		'安排':'arr',
		'开发':'dev',
		'暂停':'psd',
		'测试':'tst',
		'验收':'acc',
		'发布':'pub',
	}

	@classmethod
	def _name2col(cls, name:str, addon='')->str:
		n = name[:2]
		strn = cls.NAMES[n] if n in cls.NAMES else n
		return f'{strn}_usr{addon}'

	

class F1To1CN(models.OneToOneField):
	'''
	F: Field 1 To 1
	C: Cascade 一并删除子
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
	C: Cascade 一并删除子
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