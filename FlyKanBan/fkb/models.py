from typing import Any

from FlyKanBan.db_type.internal_fields import *

from fkb.mod_type import *
from fkb.mod_calc import *
from fkb.mod_fixed import *

class Relation(models.Model):
	art_a = KC('Artifact', '主制品', 'rel_a')
	rlt = FSttN('关系类型', RELATION)
	art_b = KC('Artifact', '被关联制品', 'rel_b')
	rdr = FUIntN('顺序(b在a中的顺序)') # 0, 1, 2, 3, ... 越小越靠前

	def __str__(self) -> str:
		return f'{self.art_a}>{self.rlt}>{self.art_b}'
	
	def __hash__(self) -> int:
		return self.__str__().__hash__()
	
	def __eq__(self, __value: object) -> bool:
		if isinstance(__value, Relation):
			return self.art_a == __value.art_a and\
				   self.rlt == __value.rlt and\
				   self.art_b == __value.art_b
		return super().__eq__(__value)

	class Meta():
		indexes = [
			Index('art_a'),
			Index('art_b'),
		]

class IdxAS(Index):
	def __init__(self, *args, **kwargs):
		kwargs['add'] = 'AS'
		super().__init__(*args, **kwargs)

class UsrAS(KUserND):
	def __init__(self, *args, **kwargs):
		if args:
			name = args[0]
			kwargs['verbose_name'] = name
		kwargs['add'] = 'AS'
		super().__init__(**kwargs)
   
class ArtStage(models.Model):
	''' 项目相关时间节点 '''
	art = F1To1C('Artifact', primary_key=True)

	rev_srt_tim = FDateTimeN('评审(review)开始时间(第一次)')
	rev_end_tim = FDateTimeN('评审完成时间|待安排(最后一次)')
	rev_usr = UsrAS('评审人员')
	rev_dur = FDurationN('总评审时长')

	arr_tim = FDateTimeN('安排时间')
	arr_usr = UsrAS('安排人员')

	dev_srt_tim = FDateTimeN('开发开始时间(第一次)')
	dev_end_tim = FDateTimeN('开发完成时间|待测试(最后一次)')
	dev_usr = UsrAS('开发人员')
	dev_dur_est = FDurationN('开发时长(预估)')
	dev_dur = FDurationN('总开发时长')

	psd_srt_tim = FDateTimeN('暂停开始时间(第一次)')
	psd_end_tim = FDateTimeN('暂停结束时间(最后一次)')
	psd_usr = UsrAS('暂停人员')
	psd_dur = FDurationN('总暂停时长')

	tst_srt_tim = FDateTimeN('测试开始时间(第一次)')
	tst_end_tim = FDateTimeN('测试完成时间|待验收(最后一次)')
	tst_usr = UsrAS('测试人员')
	tst_dur_est = FDurationN('测试时长(预估)')
	tst_dur = FDurationN('总测试时长')

	acc_srt_tim = FDateTimeN('验收(acceptance)开始时间(第一次)')
	acc_end_tim = FDateTimeN('验收完成时间|待发布(最后一次)')
	acc_usr = UsrAS('验收人员')
	acc_dur = FDurationN('总验收时长')

	pub_tim = FDateTimeN('发布时间|待结束')
	pub_usr = UsrAS('发布人员')

	ddl_tim = FDateTimeN('截止(deadline)时间')
	
	ver_lst = FUBigInt('版本(最新)')

	class Meta():
		indexes = [
			IdxAS('art'),
			IdxAS('rev_srt_tim'),
			IdxAS('rev_end_tim'),
			IdxAS('dev_srt_tim'),
			IdxAS('dev_end_tim'),
			IdxAS('psd_srt_tim'),
			IdxAS('psd_end_tim'),
			IdxAS('tst_srt_tim'),
			IdxAS('tst_end_tim'),
			IdxAS('acc_srt_tim'),
			IdxAS('acc_end_tim'),

			IdxAS('arr_tim'),
			IdxAS('pub_tim'),
			IdxAS('ddl_tim'),

			IdxAS('rev_dur'),
			IdxAS('dev_dur'),
			IdxAS('psd_dur'),
			IdxAS('tst_dur'),
			IdxAS('acc_dur'),

			IdxAS('rev_usr'),
			IdxAS('arr_usr'),
			IdxAS('dev_usr'),
			IdxAS('psd_usr'),
			IdxAS('tst_usr'),
			IdxAS('acc_usr'),
			IdxAS('pub_usr'),
		]

	@classmethod
	def make_pkeys(cls, art, **kwargs)->dict[str,Any]|None:
		if art is None: return None
		return {'art':art}


class Artifact(models.Model):
	''' 
	其实涵盖了所有和项目产品相关信息：
	产品类：产品，需求，BUG 等
	项目类：计划，迭代，任务 等
	本类为制品自身属性
	'''	
	# 自身属性：
	typ = FStt('类型', ARTTYPE, 'T')
	uid = FUInt('主库ID') # mostly is remote db id
	ver = FUBigInt('版本(当前)') # 用来索引的ver。如果不用来索引，使用 stg.ver_lst

	stt = FStt('状态', STATUS, '-XJ')
	sht = FChar32N('简称')
	ttl = FChar32N('标题')
	pnt = FFloatN('点数(评审)')
	pnt_est = FFloatN('点数(预估)')

	crt_tim = FDateTimeN('创建(create)时间|开始')
	crt_usr = KUserND('创建人员')
	cls_tim = FDateTimeN('关闭(close)时间|结束|取消')
	cls_usr = KUserND('关闭人员')

	rsp_usr = KUserND('负责人员')
	pri = FSttN('优先级', PRIORITY)

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

			Index('crt_tim'),
			Index('crt_usr'),
			Index('cls_tim'),
			Index('cls_usr'),
			Index('rsp_usr'),
		]

	@classmethod
	def make_pkeys(cls, typ, uid, ver=0, **kwargs)->dict[str,Any]|None:
		if typ is None: return None
		if uid is None: return None
		ret = { 'typ':typ, 'uid': uid, 'ver':ver}
		return ret

	def __str__(self):
		return f'{self.typ}#{self.uid}/{self.ver}'
	
	def __hash__(self) -> int:
		return self.__str__().__hash__()
	
	def __eq__(self, __value: object) -> bool:
		if isinstance(__value, Artifact):
			return self.typ == __value.typ and self.uid == __value.uid and self.ver == __value.ver
		
		if isinstance(__value, dict):
			has_key = False
			if 'typ' in __value:
				if self.typ != __value['typ']:return False
				has_key = True
			if 'uid' in __value:
				if self.uid != __value['uid']:return False
				has_key = True
			if 'ver' in __value:
				if self.ver != __value['ver']:return False
				has_key = True
			return has_key

		return super().__eq__(__value)
	
	def pts(self):
		pts = self.pnt_est if not self.pnt else self.pnt
		return 0 if not pts else pts
