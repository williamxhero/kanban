from fkb.models import *
from fkb.tools.util import Util
from fkb.tools.proc_table import ProcChild
from fkb.tools.fly_zentao.proc_mixin import ProcMixin

class ProcItor(ProcChild, ProcMixin):

    KEY_MAP = {
        # == inf: ==
        't1.`id`':'uid',
        't1.`name`':'_ttl',
        't1.`code`':'_sht',
        't1.`openedBy`':'_crt_usr',
        #t1.'`closedBy`':'_cls_usr',  # always null
        't1.`pri`':'_pri',
        't1.`PM`':'_rsp_usr',
        't1.`order`':'_rdr',

        # t2
        't2.`begin`':'crt_tim',
        't2.`end`':'cls_tim',
        't2.`projectCount`':'ver',
        
        # == rel: ==
        # 只处理 不同类-父 和 同类-子
        't3.`plan`':'_of_Pl',
        't1.`projects`':'_has_It',
    }

    ID_TYPE = 'It'
    
    def change_dict(self, dct):
        if self._null_dct_if_key_art_not_exist(dct, '_of_Pl'):
            return

        self._chg_stt_by_date(dct, 'crt_tim', 'cls_tim')

        if dct['ver'] > 0:
            # for other version, zentao only has date frame.
            # so only keep : uid, ver, stt, date
            pop_keys = ('ttl', 'sht', '_crt_usr', '_pri',
                        '_rsp_usr', 'rdr', '_of_Pl', '_has_It') 
            Util.pop_key(dct, *pop_keys)
        else:
            self._chg_pri(dct)
            self._chg_ttl_sht(dct)
            self._chg_usr(dct, 'rsp_usr')
            self._chg_usr(dct, 'crt_usr')

            rdr = Util.pop_key(dct, '_rdr')
            self._chg_rlt_of(dct, '_of_Pl', rdr)
            self._chg_rlt_has(dct, '_has_It')

    def db_sql(self):
        db_keys_str = ','.join(self.KEY_MAP.keys())
        sql = f'\
select {db_keys_str} \
from `zt_project` t1 \
inner join `zt_projectcount` t2 on t1.`id` = t2.`project` \
inner join `zt_projectproduct` t3 on t1.`id` = t3.`project` \
where t3.`plan`> 0 and t1.`deleted`="0" \
order by t1.`id`, t2.`projectCount` asc \
limit {self.LIMIT_ONCE} offset {self.query_offset}'
        return sql
    
    def relation_incharge(self, obj, rlt) -> bool:
        return self.relation_incharge_A(obj, rlt)