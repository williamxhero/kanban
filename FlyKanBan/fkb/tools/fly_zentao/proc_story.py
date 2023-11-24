from fkb.tools.util import Util
from fkb.models import *
from fkb.tools.sync_db.proc_table import ProcChild
from fkb.tools.fly_zentao.proc_mixin import ProcMixin
from fkb.tools.fly_zentao.proc_task import ProcTask

class ProcStory(ProcChild, ProcMixin):
    KEY_MAP = {
        # == inf: ==
        'id':'uid',
        'title':'_ttl',
        'estPts':'_pnt_est',
        'version':'_ver',
        'stage':'_stt',
        'pri':'_pri',
        'openedDate':'crt_tim',
        'openedBy':'_crt_usr',
        'closedDate':'cls_tim',
        'closedBy':'_cls_usr',

        # == stg: ==
        'reviewedDate':'_rev_end_tim',
        'reviewedBy':'_rev_usr',
        'examineDate':'_acc_end_tim',
        'examineBy':'_acc_usr',

        # == rel: ==
        # 只处理 不同类-父 和 同类-子
        'product':'_of_Pd',
    }

    SQL_TABLE_NAME = 'zt_story'
    ID_TYPE = 'S'

    STT_KV = {
        '':'-XJ',
        'write':'-XJ', # 未评审 设定中
        'finalize':'-PS', # 已评审
        'toSplit':'AP-', # 安排中（已关联迭代，待拆分任务）
        'toDevelop':'-AP', # 已安排
        'developing':'KF-', # 开发中
        'testing':'CS-', # 测试中
        'complete':'-CS', # 待验收（已测完）
        'verified':'-YS', # 已验收
        'released':'-FB', # 已发布
        'closed':'-GB', # 已关闭
    }

    def db_sql(self, limit):
        sql = f'select story from zt_task where \
id >= {ProcTask.SQL_ID_START_FROM} and story > 0 \
and `deleted` = \'0\' group by story{limit}'
        stry_ids = self.query_db_sql(sql)
        stid_lst = []
        if stry_ids:
            for str in stry_ids:
                stid_lst.append(f'{str[0]}')
            self.SQL_IDS_IN = ','.join(stid_lst)
        return super().db_sql(limit)
    
    _st_pls = None # story -> (plan, order)
    _st_its = None # story -> (itor, orddr)

    def _rearrange_ids(self, ids:list):
        ret = {}
        if not ids: return ret
        
        pl_st_id = []

        for pid, sid_str in ids:
            if not pid or not sid_str: continue
            sids = sid_str.split(',')
            if len(sids) == 0: continue

            for idx, si in enumerate(sids):
                sid = to_int(si)
                pl_st_id.append((pid, sid, idx))

        for pid, sid, idx in pl_st_id:
            v = ret.setdefault(sid, {})
            v[pid] = idx

        return ret
    
    def before_sync(self):
        results = self.query_db_sql(f'select id, storyOrder from zt_productplan where deleted = "0"')
        self._st_pls = self._rearrange_ids(results)

        results = self.query_db_sql(f'select id, storyOrder from zt_project where deleted = "0"')
        self._st_its = self._rearrange_ids(results)
    

    def change_dict(self, dct):
        # 必须有归属产品
        if self._null_dct_if_key_art_not_exist(dct, '_of_Pd'):
            return

        self._chg_pnt(dct)
        self._chg_pri(dct)
        self._chg_ttl(dct)
        self._chg_stt(dct, self.STT_KV)
        self._chg_usr(dct, 'crt_usr')
        self._chg_usr(dct, 'cls_usr')

        dct['stg'] = {
            'rev_end_tim' : Util.pop_key(dct, '_rev_end_tim'),
            'rev_usr' : self._chg_usr(dct, 'rev_usr'),
            'acc_end_tim' : Util.pop_key(dct, '_acc_end_tim'),
            'acc_usr' : self._chg_usr(dct, 'acc_usr'),
            'ver_lst' : Util.pop_key(dct, '_ver'),
        }
        
        self._chg_rlt_of(dct, '_of_Pd', None)

        # 所属 计划 和 迭代 (必须是存在的):
        sid = dct['uid']
        pls = self._st_pls.get(sid,{})
        for pl, rdr in pls.items():
            if Artifact.objects.filter(typ='Pl', uid=pl).exists():
                self._append_rlt(dct, True, 'Pl', pl, rdr)

        its = self._st_its.get(sid,{})
        for it, rdr in its.items():
            if Artifact.objects.filter(typ='It', uid=it).exists():
                self._append_rlt(dct, True, 'It', it, rdr)

        pass     
        
    def relation_incharge(self, obj, rlt) -> bool:
        return self.relation_incharge_A(obj, rlt)
