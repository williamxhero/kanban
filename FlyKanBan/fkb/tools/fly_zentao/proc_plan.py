from fkb.tools.util import Util
from fkb.models import *
from fkb.tools.proc_table import ProcChild
from fkb.tools.fly_zentao.proc_mixin import ProcMixin


class ProcPlan(ProcChild, ProcMixin):
    
    KEY_MAP = {
        # == inf: ==
        'id':'uid',
        'title':'_ttl',
        'begin':'crt_tim',
        'end':'cls_tim',

        # == rel: ==
        # 只处理 不同类-父 和 同类-子
        'product':'_of_Pd',
        'productplans':'_has_Pl',
    }

    TABLE_NAME = 'zt_productplan'
    ID_TYPE = 'Pl'
    _rdrs = {}

    def _load_rdrs(self):
        if self._rdrs:
            return
        results = self.query_db_sql(f'select id, plan_ids from zt_product where deleted = "0"')
        for result in results:
            pdid = result[0]
            if not result[1]: continue
            sub_ids = result[1].split(',')
            if len(sub_ids) == 0: continue
            for idx, si in enumerate(sub_ids):
                sid = to_int(si)
                if sid == 0: continue
                self._rdrs[sid] = (pdid, idx)

    def change_dict(self, dct):
        if self._null_dct_if_key_art_not_exist(dct, '_of_Pd'):
            return

        self._load_rdrs()
        rdr = self._rdrs.get(dct['uid'], (None, None))

        self._chg_ttl(dct)
        self._chg_stt_by_date(dct, 'crt_tim', 'cls_tim')
        self._chg_rlt_of(dct, '_of_Pd', rdr[1])
        self._chg_rlt_has(dct, '_has_Pl')

    def relation_incharge(self, obj, rlt) -> bool:
        return self.relation_incharge_A(obj, rlt)

