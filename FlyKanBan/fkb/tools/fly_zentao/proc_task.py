from fkb.models import *
from fkb.tools.util import Util, Print
from fkb.tools.sync_db.proc_table import ProcChild
from fkb.tools.fly_zentao.proc_mixin import ProcMixin

class ProcTask(ProcChild, ProcMixin):
    
    KEY_MAP = {
        # == inf: ==
        'id':'uid',
        'name':'ttl',
        'pri':'_pri',
        'status':'_stt',

        'storyPoint':'_pnt',
        'estPoint':'_pnt_est',

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
        'finishedBy':'_fi_usr', 
        'realStartedBy':'_rs_usr',
        'assignedTo':'_to_usr',
        # -
        
        'lastPausedDate':'_psd_srt_tim',
        'pausedHr':'_psd_dur', # hour to timespan

        # == rel: == 
        # 处理所有 本体是子类的关系
        'project':'_of_It',
        'story':'_of_S',
        'parent':'_of_T',
    }

    SQL_TABLE_NAME = 'zt_task'
    SQL_ID_START_FROM = 6879
    ID_TYPE = 'T'
    STT_KV = {
        'wait':'-AP',
        'doing':'KF-',
        'pause':'KFX',
        'done':'-KF',
        'cancel':'-QX',
        'closed':'-GB',
    }

    def change_dict(self, dct):
        if self._null_dct_if_key_art_not_exist(dct, '_of_It'):
            return
        if self._null_dct_if_key_art_not_exist(dct, '_of_S'):
            return

        self._chg_pri(dct)
        self._chg_pnt(dct)
        self._chg_stt(dct, self.STT_KV)
        self._chg_usr(dct, 'crt_usr')

        tst_end_tim = Util.get_key(dct, '_cls_tim')
        tst_usr = self._pop_usr(dct, 'cls_usr', pop=False)

        self._chg_key(dct, 'cls_tim', 'ccl_tim', 'cls_tim')
        self._chg_usr(dct, 'cls_usr', 'ccl_usr', 'cls_usr')
        rsp_usr = self._chg_usr(dct, 'rsp_usr', 'fi_usr', 'rs_usr', 'to_usr')

        dev_dur_hr_est = Util.pop_key(dct, '_dev_dur_est')
        dev_srt_tim = Util.pop_key(dct, '_dev_srt_tim')
        dev_end_tim = Util.pop_key(dct, '_dev_end_tim')
        psd_srt_tim = Util.pop_key(dct, '_psd_srt_time')
        psd_dur_hr = Util.pop_key(dct, '_psd_dur')
        dv_dur_hr = Util.calc_work_dur(dev_srt_tim, dev_end_tim, psd_dur_hr)
        # 从开发完成到 测试完成，就是测试时长
        tst_dur_hr = Util.calc_work_dur(dev_end_tim, tst_end_tim)

        dct['stg'] = {
            # 任务的开发和测试时间是重点。
            'dev_dur_est':self._hr2dur(dev_dur_hr_est),
            'dev_srt_tim':dev_srt_tim,
            'dev_end_tim':dev_end_tim,
            'dev_dur':dv_dur_hr,
            'dev_usr':rsp_usr,

            # 最后一次开始暂停时间。结束时间未知。
            'psd_srt_tim':psd_srt_tim,
            'psd_dur':self._hr2dur(psd_dur_hr),
            
            # 任务 测试完成，就算完成了
            'tst_srt_tim':dev_end_tim,
            'tst_end_tim':tst_end_tim,
            'tst_usr':tst_usr,
            'tst_dur':tst_dur_hr,
        }

        self._chg_rlt_of(dct, '_of_It', None)
        self._chg_rlt_of(dct, '_of_S', None)
        self._chg_rlt_of(dct, '_of_T', None)


    def relation_incharge(self, obj, rlt) -> bool:
        return self.relation_incharge_B(obj, rlt)
            
