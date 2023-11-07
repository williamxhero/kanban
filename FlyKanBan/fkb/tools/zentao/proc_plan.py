from fkb.models import *
from fkb.tools.proc_table import ProcChild
from fkb.tools.zentao.proc_mixin import ProcMixin


class ProcPlan(ProcChild, ProcMixin):
    
    KEY_MAP = {
        # self
        'id':'uid',
        'title':'_ttl',
        'begin':'crt_tim',
        'end':'cls_tim',
        # rel # 只处理 不同类父 和 同类子
        'product':'_of_Pd',
        'productplans':'_has_Pl',
    }

    TABLE_NAME = 'zt_productplan'
    ID_TYPE = 'Pl'

    def change_dict(self, dct):
        self._chg_ttl(dct)
        self._chg_stt_by_date(dct, 'crt_tim', 'cls_tim')
        self._chg_rlt_of(dct, '_of_Pd')
        self._chg_rlt_has(dct, '_has_Pl')



