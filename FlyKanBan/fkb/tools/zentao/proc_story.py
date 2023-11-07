import json
from fkb.tools.util import Util
from fkb.models import *
from fkb.tools.proc_table import ProcChild
from fkb.tools.zentao.proc_mixin import ProcMixin

class ProcStory(ProcChild, ProcMixin):
    KEY_MAP = {
        'id':'uid',
        'title':'_ttl',
        'estPts':'pnt_est',
        'version':'ver',
        'stage':'_stt',
        'pri':'_pri',
        'openedDate':'crt_tim',
        'openedBy':'_crt_usr',
        'closedDate':'cls_tim',
        'closedBy':'_cls_usr',

        # rel: # 只处理 不同类父 和 同类子
        'product':'_of_Pd',
        'plan':'_of_Pl',

        'childStories':'_has_St',
        #'linkStories':'_str_lnk',

        'reviewedDate':'_rev_end_tim',
        'revewedBy':'_rev_usr',
        'examinedDate':'_acc_end_tim',
        'examinedBy':'_acc_usr',
    }

    TABLE_NAME = 'zt_story'
    ID_START_FROM = 6879
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

    def change_dict(self, dct):
        self._chg_pri(dct)
        self._chg_ttl(dct)
        self._chg_stt(dct, self.STT_KV)
        self._chg_usr(dct, 'crt_usr')
        self._chg_usr(dct, 'cls_usr')
        self._chg_usr(dct, 'rev_usr')
        self._chg_usr(dct, 'acc_usr')

        self._chg_rlt_of(dct, '_of_Pd')
        self._chg_rlt_of(dct, '_of_Pl')
        self._chg_rlt_has(dct, '_has_St')

        dct['stg'] = {
            'rev_end_time' : Util.pop_key(dct, '_rev_end_tim'),
            'acc_end_time' : Util.pop_key(dct, '_acc_end_tim'),
        }
