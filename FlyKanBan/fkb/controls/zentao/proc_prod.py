from fkb.models import *
from fkb.controls.proc_table import ProcChild
from fkb.controls.zentao.proc_mixin import ProcPriMixin



class ProcProd(ProcChild, ProcPriMixin):
    
    KEY_MAP = {
        'id':'uid',

        'name':'ttl',
        'code':'sht',
        'createdDate':'crt_tim',
        'order':'rdr',

        # need to convert
        'status':'_stt',
        'pri':'_pri',
        'PO':'_rsp_usr',

        # rel:
        'products':'_pds_has',
        }
    
    STT_KV = {
        'normal':'KF-', # 进行中
        'closed':'-GB', # 已关闭
    }

    TABLE_NAME = 'zt_product'
    ID_TYPE = 'Pd'

    def change_dict(self, dct):
        self._chg_pri(dct)
        self._chg_stt(dct, self.STT_KV)
        self._chg_usr(dct, 'rsp_usr')
        self._chg_children(dct, '_pds_has')
