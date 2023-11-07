from fkb.models import *
from fkb.tools.proc_table import ProcChild
from fkb.tools.zentao.proc_mixin import ProcMixin



class ProcProd(ProcChild, ProcMixin):
    
    KEY_MAP = {
        'id':'uid',

        'name':'_ttl',
        'code':'_sht',
        'createdDate':'crt_tim',
        'order':'rdr',

        # need to convert
        'status':'_stt',
        'pri':'_pri',
        'PO':'_rsp_usr',

        # rel: # 只处理 不同类父（没有） 和 同类子
        'products':'_has_Pd',
        }
    
    STT_KV = {
        'normal':'KF-', # 进行中
        'closed':'-GB', # 已关闭
    }

    TABLE_NAME = 'zt_product'
    ID_TYPE = 'Pd'

    def change_dict(self, dct):
        self._chg_pri(dct)
        self._chg_ttl_sht(dct)
        self._chg_stt(dct, self.STT_KV)
        self._chg_usr(dct, 'rsp_usr')
        self._chg_rlt_has(dct, '_has_Pd')
