from typing import Any

from FlyKanBan.db_type.internal_fields import *
from FlyKanBan.db_type.version4_field import FVer

from fkb.models import Artifact
from fkb.mod_type import *


class Version(models.Model):
	'''
	版本
	'''
	pd = KD(Artifact, 'product', 'ver_pd')
	ver = FVer('版本号')
	pst_fix = FChar32N('后缀(alpha,beta,release)')
	nxt_ver = KD('Version', 'next_ver', 'ver_next')
	pck_dt = FDateTimeN('打包时间')
	rls_dt = FDateTimeN('发布时间')
	stys = FNToNN(Artifact)
	bugs_inc = FNToNN(Artifact)
	bugs_fix = FNToNN(Artifact)

	class Meta():
		constraints =[
			models.UniqueConstraint(fields=['pd', 'ver', 'pst_fix'], name='unique_art_id')
		]
		indexes = [
			Index('pd'),
			Index('pd', 'ver'),
			Index('nxt_ver'),
		]
