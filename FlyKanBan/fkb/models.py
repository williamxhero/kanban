from datetime import datetime, date as dt_date
from typing import Any, TypeVar

from FlyKanBan.db_type.internal_fields import *
from FlyKanBan.db_type.version4_field import FVer


def is_some(v:Any): 
	return v is not None

def get_val(val:Any)->Any:
	if isinstance(val, (datetime, dt_date)):
		if val.year == 0 or val.year >= 3000:
			val = None
	return val

def str_date(val:str|None):
	if val is None:
		return None
	return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')

ARTTYPE: list[tuple[str,str]] = [
	('Pd', '产品'),
	('Pl', '计划'),
	('It', '迭代'),
	('R', '需求'),
	('T', '任务'),
	('B', 'BUG'),
]

STATUS: list[tuple[str,str]] = [
	# 待，中，已
	('XJ-', '编辑中|新建中'),
	('-XJ', '已新建|待评审'),

	('-QX', '已取消'),
	('-ZT', '已暂停'),

	('PS-', '评审中'),
	('-PS', '已评审|待安排'),
	('AP-', '安排中'),
	('-AP', '已安排|待开发|待开始|待修复'),
	('KF-', '开发中|进行中'),
	('-KF', '已开发|已修复|待测试'),
	('CS-', '测试中'),
	('-CS', '已测试|待验收'),
	('YS-', '验收中'),
	('-YS', '已验收|已完成|待发布|待关闭'), # 还可以 发布 和 关闭，就选择这个
	('-FB', '已发布'),
	('-GB', '已关闭|已结束'), # 再没任何操作，就选择这个
]

PRIORITY: list[tuple[str,str]] = [
	('LO-', '低-'),
	('LO', '低'),
	('MI-', '中-'),
	('MI', '中'),
	('MI+', '中+'),
	('HI', '高'),
	('HI+', '高+'),
]

RELATION: list[tuple[str,str]] = [
	('', 'a知道b'),
	('CN', 'a包含b'),
	('SE', 'a结束b开始'),
	('SS', 'a开始b开始'),
	('EE', 'a结束b结束'),
	('ES', 'a开始b结束'),
]


class User(models.Model):
	act = FChar32('账号', unique=True, primary_key=True)
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
	def make_pkeys(cls, **kv:Any)->dict[str,Any]|None:
		if 'act' not in kv: return None
		return {'act':kv['act']}
	
	def __eq__(self, __value: object) -> bool:
		if isinstance(__value, dict):
			if 'act' in __value:
				return self.act == __value['act']

		return super().__eq__(__value)
	
	def __str__(self):
		return f'[U]{self.nam}({self.act})'

class Relation(models.Model):
	art_a = KC('Artifact', '主制品', 'art_a')
	rlt = FStatus('关系类型', RELATION, '')
	art_b = KC('Artifact', '被关联制品', 'art_b')

	def __str__(self) -> str:
		return f'{self.art_a}>{self.rlt}>{self.art_b}'
	
	class Meta():
		indexes = [
			Index('art_a'),
			Index('art_b'),
		]

class ArtStage(models.Model):
	''' 项目相关时间节点 '''
	art = F1To1C('Artifact', primary_key=True)

	rev_srt_tim = FDateTimeN('评审(review)开始时间(第一次)')
	rev_end_tim = FDateTimeN('评审完成时间|待安排(最后一次)')
	rev_usr = KUserND('评审人员', 'rev_usr')
	rev_dur = FDurationN('总评审时长')

	arr_tim = FDateTimeN('安排时间')
	arr_usr = KUserND('安排人员', 'arr_usr')

	dev_srt_tim = FDateTimeN('开发开始时间(第一次)')
	dev_end_tim = FDateTimeN('开发完成时间|待测试(最后一次)')
	dev_usr = KUserND('开发人员', 'dev_usr')
	dev_dur_est = FDurationN('开发时长(预估)')
	dev_dur = FDurationN('总开发时长')

	psd_srt_time = FDateTimeN('暂停开始时间(第一次)')
	psd_end_time = FDateTimeN('暂停结束时间(最后一次)')
	psd_usr = KUserND('暂停人员', 'psd_usr')
	psd_dur = FDurationN('总暂停时长')

	tst_srt_tim = FDateTimeN('测试开始时间(第一次)')
	tst_end_tim = FDateTimeN('测试完成时间|待验收(最后一次)')
	tst_usr = KUserND('测试人员', 'tst_usr')
	tst_dur_est = FDurationN('测试时长(预估)')
	tst_dur = FDurationN('总测试时长')

	acc_srt_tim = FDateTimeN('验收(acceptance)开始时间(第一次)')
	acc_end_tim = FDateTimeN('验收完成时间|待发布(最后一次)')
	acc_usr = KUserND('验收人员', 'acc_usr')
	acc_dur = FDurationN('总验收时长')

	pub_tim = FDateTimeN('发布时间|待结束')
	pub_usr = KUserND('发布人员', 'pub_usr')

	class Meta():

		indexes = [
			Index('art'),
			Index('rev_srt_tim'),
			Index('rev_end_tim'),
			Index('dev_srt_tim'),
			Index('dev_end_tim'),
			Index('psd_srt_time'),
			Index('psd_end_time'),
			Index('tst_srt_tim'),
			Index('tst_end_tim'),
			Index('acc_srt_tim'),
			Index('acc_end_tim'),

			Index('arr_tim'),
			Index('pub_tim'),

			Index('rev_dur'),
			Index('dev_dur'),
			Index('psd_dur'),
			Index('tst_dur'),
			Index('acc_dur'),

			Index('rev_usr'),
			Index('arr_usr'),
			Index('dev_usr'),
			Index('psd_usr'),
			Index('tst_usr'),
			Index('acc_usr'),
			Index('pub_usr'),
		]

	@classmethod
	def make_pkeys(cls, **kv:Any)->dict[str,Any]|None:
		if 'art' not in kv: return None
		return {'art':kv['art']}

class Artifact(models.Model):
	''' 
	其实涵盖了所有和项目产品相关信息：产品，计划，迭代，需求，任务，BUG等等
	'''	
	# 自身属性：
	typ = FStatus('类型', ARTTYPE, 'T')
	uid = FUInt('主库ID') # mostly is remote db id
	ver = FVer('版本')

	sht = FChar32N('简称')
	ttl = FChar32('标题')
	
	stt = FStatus('状态', STATUS, 'XJ-')
	pri = FStatus('优先级', PRIORITY, 'MI')
	rdr = FUIntN('顺序')
	pnt = FFloatN('点数(评审)')
	pnt_est = FFloatN('点数(预估)')

	rsp_usr = KUserND('负责人员', 'rsp_usr')
	ddl_tim = FDateTimeN('截止(deadline)时间')

	crt_tim = FDateTimeN('创建(create)时间|开始')
	crt_usr = KUserND('创建人员', 'crt_usr')

	cls_tim = FDateTimeN('关闭(close)时间|结束|取消')
	cls_usr = KUserND('关闭人员', 'cls_usr')

	stg = F1To1CN(ArtStage)
	rlt = FNToNN('self', Relation) # 相关联制品

	class Meta():
		constraints =[
			models.UniqueConstraint(fields=['typ', 'uid', 'ver'], name='unique_art_id')
		]
		indexes = [
			Index('typ'),
			Index('typ', 'uid'),
			Index('typ', 'uid', 'ver'),
			Index('stt'),
			Index('pri'),
			Index('pnt_est'),

			Index('rsp_usr'),
			Index('ddl_tim'),

			Index('crt_tim'),
			Index('crt_usr'),
			Index('cls_tim'),
			Index('cls_usr'),
		]

	@classmethod
	def make_pkeys(cls, **kv:Any)->dict[str,Any]|None:
		if 'typ' not in kv: return None
		if 'uid' not in kv: return None
		ret = { 'typ':kv['typ'], 'uid': kv['uid']}

		if 'ver' in kv and is_some(kv['ver']):
			ret['ver'] = kv['ver']
		return ret
	
	def __str__(self):
		if self.ver == '0':
			return f'[A]{self.typ}#{self.uid}'
		return f'[A]{self.typ}#{self.uid}/{self.ver}'

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