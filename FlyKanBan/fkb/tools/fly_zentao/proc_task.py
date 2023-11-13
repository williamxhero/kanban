
from work_hours import WorkHours

from fkb.tools.util import Util
from fkb.models import *
from fkb.tools.proc_table import ProcChild
from fkb.tools.fly_zentao.proc_mixin import ProcMixin

class ProcTask(ProcChild, ProcMixin):
    
    KEY_MAP = {
        # == inf: ==
        'id':'uid',
        'name':'ttl',
        'pri':'_pri',
        'status':'_stt',

        'storyPoint':'pnt',
        'estPoint':'pnt_est',

        'openedDate':'crt_tim',
        'openedBy':'_crt_usr',

        # 2 choose 1 as closed
        'closedDate':'_cls_tim',
        'canceledDate':'_ccl_tim',
        'closedBy':'_cls_usr',
        'canceledBy':'_ccl_usr',
        # -

        'deadline':'ddl_tim',

        # == stg: ==
        'startEstimate':'_dev_dur_est',
        'realStarted':'_dev_srt_tim',
        'finishedDate':'_dev_end_tim',

        # n choose 1 as dev_usr/rsp_usr
        'realStartedBy':'_rs_usr',
        'assignedTo':'_to_usr',
        'finishedBy':'_fi_usr', 
        # -
        
        'lastPausedDate':'_psd_srt_time',
        'pausedHr':'_psd_dur', # hour to timespan

        # == rel: == 
        # 处理所有 本体是子类的关系
        'project':'_of_It',
        'story':'_of_S',
        'parent':'_of_T',
    }

    TABLE_NAME = 'zt_task'
    ID_START_FROM = 6879
    ID_TYPE = 'T'
    STT_KV = {
        'wait':'-AP',
        'doing':'KF-',
        'done':'-KF',
        'pause':'-ZT',
        'cancel':'-QX',
        'closed':'-GB',
    }

    wh = WorkHours()

    def _calc_dur_hr(self, start_dt, end_dt, psd_hr):
        if not start_dt or not end_dt:
            return 0
        dv_dur = self.wh.calc(start_dt, end_dt)
        dv_dur -= to_int(psd_hr)
        return dv_dur

    def change_dict(self, dct):
        if self._null_dct_if_key_art_not_exist(dct, '_of_It'):
            return
        if self._null_dct_if_key_art_not_exist(dct, '_of_S'):
            return
        
        self._chg_pri(dct)
        self._chg_stt(dct, self.STT_KV)
        self._chg_usr(dct, 'crt_usr')

        cls_tim = self._chg_key(dct, 'cls_tim', 'ccl_tim', 'cls_tim')
        cls_usr = self._chg_usr(dct, 'cls_usr', 'ccl_usr', 'cls_usr')
        rsp_usr = self._chg_usr(dct, 'rsp_usr', 'rs_usr', 'fi_usr', 'to_usr')

        dev_dur_hr_est = Util.pop_key(dct, '_dev_dur_est')
        dev_srt_tim = Util.pop_key(dct, '_dev_srt_tim')
        dev_end_tim = Util.pop_key(dct, '_dev_end_tim')
        psd_srt_time = Util.pop_key(dct, '_psd_srt_time')
        psd_dur_hr = Util.pop_key(dct, '_psd_dur')
        dv_dur_hr = self._calc_dur_hr(dev_srt_tim, dev_end_tim, psd_dur_hr)
        
        dct['stg'] = {
            # 创建时间 即为 评审时间
            'rev_end_tim':dct['crt_tim'], 
            'dev_dur_est':self._hr2dur(dev_dur_hr_est),
            'dev_srt_tim':dev_srt_tim,
            'dev_end_tim':dev_end_tim,
            'dev_dur':self._hr2dur(dv_dur_hr),
            'dev_usr':rsp_usr,
            'psd_srt_time':psd_srt_time,
            'psd_dur':self._hr2dur(psd_dur_hr),
            # 关闭时间 即为 验收时间
            'acc_end_tim':cls_tim,
            'acc_usr':cls_usr,
        }

        self._chg_rlt_of(dct, '_of_It', None)
        self._chg_rlt_of(dct, '_of_S', None)
        self._chg_rlt_of(dct, '_of_T', None)


    def relation_incharge(self, obj, rlt) -> bool:
        return self.relation_incharge_B(obj, rlt)