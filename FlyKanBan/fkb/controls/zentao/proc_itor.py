from fkb.models import *
from fkb.controls.proc_table import ProcChild
from fkb.controls.zentao.proc_mixin import ProcPriMixin, ProcSttByDateMixin

class ProcItor(ProcChild, ProcPriMixin, ProcSttByDateMixin):

    KEY_MAP = {
        # self
        'id':'uid',
        'name':'ttl',
        'code':'sht',
        'begin':'crt_tim',
        'openedBy':'_crt_usr',
        'end':'cls_tim',
        'closedBy':'_cls_usr',

        'pri':'_pri',
        'PM':'_rsp_usr',
        'order':'rdr',

        # rel
        'projects':'_itr_has',
    }

    TABLE_NAME = 'zt_project'
    ID_TYPE = 'It'
    
    def change_dict(self, dct):
        self._chg_pri(dct)
        self._chg_stt_by_date(dct, 'crt_tim', 'cls_tim')
        self._chg_usr(dct, 'rsp_usr')
        self._chg_usr(dct, 'crt_usr')
        self._chg_usr(dct, 'cls_usr')
        self._chg_children(dct, '_itr_has')

    def db_sql(self):
        col_names = list(self.KEY_MAP.keys())
        db_keys = []
        for key in col_names:
            if key == 'begin' or key == 'end':
                db_keys.append('t2.`{key}`')
            else:
                db_keys.append('t1.`{key}`')
        db_keys.append('t2.`projectCount` as `ver`')
        db_keys_str = ','.join(db_keys)
        sql = f'select {db_keys_str} from `{self.TABLE_NAME}` `deleted`="0" order by `id`, `ver` asc offset {self.query_offset}'
        return sql

class ProcPdPlIt(ProcTable):
    ''' 建立产品、计划、迭代的关系 '''

    def __init__(self):
        self.DB_SQL = self.db_sql

    def db_sql(self):
        id_key = list(db_keys_str)[0]
        whr_id = f'`{id_key}`>="{key_start}"' if key_start else None
        whr_del = '`deleted`="0"' if has_delete else None
        where = self.sql_where(whr_del, whr_id)
        sql = f'select {db_keys_str} from `{tbl_nam}` {where} order by `{id_key}` asc limit 500'
        return sql

    def change_dict(self, dct):
        ...
