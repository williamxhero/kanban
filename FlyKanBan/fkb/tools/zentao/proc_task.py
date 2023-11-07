
from work_hours import WorkHours

from fkb.models import *
from fkb.tools.proc_table import ProcTable

class ProcTask(ProcTable):
    
    KEY_MAP = {
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
        #'assignedDate':'_arr_tim', # if task is closed，it's closedDate

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

        # rel: # 只处理 不同类父 和 同类子
        'parent':'_parent',
        'project':'_itor',
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

    def _calc_dur_hr(self, start_str, end_str, psd_hr):
        if start_str is None: return 0
        if end_str is None: return 0
        srt_time = str_date(start_str)
        end_time = str_date(end_str)
            
        dv_dur = self.wh.calc(srt_time, end_time)
        dv_dur -= psd_hr
        return dv_dur

   
    def change_dict(self, dct):
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
            'dev_dur_est':self._hr2dur(dev_dur_hr_est),
            'dev_srt_tim':dev_srt_tim,
            'dev_end_tim':dev_end_tim,
            'dev_dur':self._hr2dur(dv_dur_hr),
            'dev_usr':rsp_usr,
            'psd_srt_time':psd_srt_time,
            'psd_dur':self._hr2dur(psd_dur_hr),
            'acc_end_tim':cls_tim,
            'acc_usr':cls_usr,
        }

        prt_uid = Util.pop_key(dct, '_parent')
        itr_uid = Util.pop_key(dct, '_itor')
        dct['rlt'] = [
            {'typ': 'T', 'art_a' : prt_uid, 'rlt':'CN'},
            {'typ': 'It', 'art_a' : itr_uid, 'rlt':'CN'}
        ]
        


