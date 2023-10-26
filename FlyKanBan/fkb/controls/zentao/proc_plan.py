from datetime import date
from fkb.models import *
from fkb.controls.proc_table import ProcChild
from fkb.controls.zentao.proc_mixin import ProcSttByDateMixin


class ProcPlan(ProcChild, ProcSttByDateMixin):
    
    KEY_MAP = {
        # self
        'id':'uid',
        'title':'ttl',
        'begin':'crt_tim',
        'end':'cls_tim',
        # rel
        'productplans':'_pls_has',
    }

    TABLE_NAME = 'zt_productplan'
    ID_TYPE = 'Pl'

    def change_dict(self, dct):
        self._chg_stt_by_date(dct, 'crt_tim', 'cls_tim')
        self._chg_children(dct, '_pls_has')


