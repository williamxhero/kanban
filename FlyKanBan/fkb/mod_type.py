from typing import Any

from datetime import datetime, date


def to_int(v:Any):
	try:
		return int(v)
	except:
		return 0

def is_some(v:Any): 
	return v is not None

def get_val(val:Any)->Any:
	if isinstance(val, date):
		if val.year == 0 or val.year >= 3000:
			val = None
	if isinstance(val, str):
		val = val.strip()
		if len(val) == 0:
			val = None
	return val

def str_date(val:str|None):
	if val is None:
		return None
	return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')

WORKTYPE: list[tuple[str,str]] = [
	('PK', '评审完->开发完'),
	('PC', '评审完->测试完'),
	('PY', '评审完->验收完'),

	('K', '开发效率'),
	('KC', '开发完->测试完'),
	('C', '测试效率'),
	('CY', '测试完->验收完'),
]

ARTTYPE: list[tuple[str,str]] = [
	('Pd', '产品'),
	('Pl', '计划'),
	('It', '迭代'),
	('R', '需求'),
	('T', '任务'),
	('B', 'BUG'),
]

STATUS: list[tuple[str,str]] = [
	# -已，中-(待)
	# ---
	('-XJ', '已新建|待评审|设定中'),
	# 随时可以 取消 ->
	('-QX', '已取消'),
	# OO中可以 暂停 ->  开发中暂停：KFX
	('X', '已暂停'),
	# ---
	('PS-', '评审中'),
	('-PS', '已评审|待安排'),
	('AP-', '安排中|已关联'),
	('-AP', '已安排|待开发|待开始|待修复'),
	('KF-', '开发中|进行中'),
	('-KF', '已开发|已修复|待测试'),
	('CS-', '测试中'),
	('-CS', '已测试|待验收'),
	('YS-', '验收中'),
	# 还可以 发布 和 关闭，就选择这个 ->
	('-YS', '已验收|已完成|待发布|待关闭'), 
	('-FB', '已发布'),
	# 后续再没任何操作，就选择这个 ->
	('-GB', '已关闭|已结束'), 
]

PRIORITY: list[tuple[str,str]] = [
	('LO_', '低-'),
	('LO', '低'),
	('MI-', '中-'),
	('MI', '中'),
	('MIT', '中+'),
	('HI', '高'),
	('HIT', '高+'),
]

RELATION: list[tuple[str,str]] = [
	('', 'a知道b'), 
	('CN', 'a包含b'), # ContaiN
	('ES', 'a结束b开始'), # End Start
	('SS', 'a开始b开始'),
	('EE', 'a结束b结束'),
	('SE', 'a开始b结束'),
]
