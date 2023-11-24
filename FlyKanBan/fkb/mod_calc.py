from FlyKanBan.db_type.internal_fields import *
from fkb.mod_type import *

class IdxCAS(Index):
	def __init__(self, *args, **kwargs):
		kwargs['add'] = 'CAS'
		super().__init__(*args, **kwargs)

class UsrCAS(KUserND):
	def __init__(self, *args, **kwargs):
		if args:
			name = args[0]
			kwargs['verbose_name'] = name
		kwargs['add'] = 'CAS'
		super().__init__(**kwargs)

class IdxPf(Index):
	def __init__(self, *args, **kwargs):
		kwargs['add'] = 'Pf'
		super().__init__(*args, **kwargs)


class Perf(models.Model):
	usr = KUserND('评测人员')
	typ = FStt('人员类型', WORKTYPE, 'YF')
	tim = models.DateField('时间')
	spd = FFloatN('速度')
	ave_spd = FFloatN('平均速度')
	dur = FDurationN('时长')
	ave_dur = FDurationN('平均时长')
	class Meta():
		constraints =[
			models.UniqueConstraint(fields=['usr', 'typ', 'tim'], name='uni_usr_typ_tim')
		]

		indexes = [
			IdxPf('usr'),
			IdxPf('typ'),
			IdxPf('usr', 'typ', 'tim'),
		]


