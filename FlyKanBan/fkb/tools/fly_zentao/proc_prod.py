from fkb.tools.util import Util
from fkb.models import *
from fkb.tools.proc_table import ProcChild
from fkb.tools.fly_zentao.proc_mixin import ProcMixin

class ProcEntry(ProcChild, ProcMixin):
    KEY_MAP = {
        'id':'uid',
    }

    def db_sql(self):
        sql = f'select 1'
        return sql

    ID_TYPE = '**'


class ProcProd(ProcChild, ProcMixin):
    
    KEY_MAP = {
        # == inf: ==
        'id':'uid',
        'name':'_ttl',
        'code':'_sht',
        'createdDate':'crt_tim',
        'order':'_rdr',

        # need to convert
        'status':'_stt',
        'pri':'_pri',
        'PO':'_rsp_usr',

        # == rel: ==
        # 只处理 不同类-父 和 同类-子
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

        dct['_of_**'] = 1
        rdr = Util.pop_key(dct, '_rdr')
        self._chg_rlt_of(dct, '_of_**', rdr)
        
    def relation_incharge(self, obj, rlt) -> bool:
        return self.relation_incharge_A(obj, rlt)