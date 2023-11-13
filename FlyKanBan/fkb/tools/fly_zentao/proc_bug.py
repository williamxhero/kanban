from fkb.models import *
from fkb.tools.proc_table import ProcTable

class ProcBug(ProcTable):
    
    KEY_MAP = {
        'id':'uid',
        'title':'_ttl',
        'pri':'_pri',
        'status':'_stt',

        'openedDate':'crt_tim',
        'openedBy':'_crt_usr',
        'closedDate':'cls_tim',
        'closedBy':'_cls_usr',
        'makeBy':'_rsp_usr', 

        'deadline':'ddl_tim',

        # 只处理 不同类父 和 同类子
    }

    STT_KV:dict[str,str] = {
        'active':'-AP',
        'resolved':'-KF',
        'closed':'-GB',
    }
    TABLE_NAME = 'zt_bug'
    ID_START_FROM = 8118
    ID_TYPE = 'B'

    def change_dict(self, dct:dict[str,Any]):
        self._chg_ttl(dct)
        self._chg_pri(dct)
        self._chg_stt(dct, self.STT_KV)
        self._chg_usr(dct, 'crt_usr')
        cls_usr = self._chg_usr(dct, 'cls_usr')
        rsp_usr = self._chg_usr(dct, 'rsp_usr')
        if rsp_usr is None:
            dct['rsp_usr'] = cls_usr

