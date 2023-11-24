# 通过 fkb 库中的表，计算出额外信息，如 团队速度，计划完成率 等等
from datetime import datetime, timedelta

from fkb.tools.util import Util, Print
from fkb.controls.util import load_children
from fkb.models import *

def _sign_if_ne(obj, att, var_from):
    if hasattr(obj, att):
        var_to = getattr(obj, att)
    else:
        var_to = None

    if var_to != var_from:
        setattr(obj, att, var_from)
        return True
    
    return False

def _calc_sty_pnt(sty, tsks, chgd):
    pnt = 0
    for tsk in tsks:
        pnt += tsk.pts()
    chgd = _sign_if_ne(sty, 'pnt', pnt) or chgd
    return chgd

class CalcData():
    _last_dt = datetime(9999,12,31)
    _frst_dt = datetime(1,1,1)

    def _stt_0(self, stg, stry, chgd):
        # ddl_tim / 截止(deadline)时间 
        #   / X
        # ver_lst / 版本(最新) 
        #   / 已有
        # rev_srt_tim / 评审(review)开始时间(第一次) 
        #   / 故事的创建时间，就是开始评审时间
        chgd = _sign_if_ne(stg, 'rev_srt_tim', stry.crt_tim) or chgd
        return chgd

    def _stt_2(self, stg, stry, chgd):
        # rev_end_tim / 评审完成时间|待安排(最后一次) 
        #   / 已有
        rev_end_tim = stry.stg.rev_end_tim
        # rev_usr / 评审人员 
        #   / 已有
        # rev_dur / 总评审时长 
        #   / 完成 - 开始
        rev_dur = Util.calc_work_dur(stg.rev_srt_tim, rev_end_tim)
        chgd = _sign_if_ne(stg, 'rev_dur', rev_dur) or chgd
        return chgd
    
    def _stt_3(self, stg, tsks, chgd):
        # first create time
        tsk = sorted(tsks, key=lambda tsk:tsk.crt_tim)[0]
        # arr_tim / 安排时间 
        #   / 放入迭代，创建了第一个任务，就算安排了
        chgd = _sign_if_ne(stg, 'arr_tim', tsk.crt_tim) or chgd
        # arr_usr / 安排人员 
        #   / 第一个任务的创建人
        chgd = _sign_if_ne(stg, 'arr_usr', tsk.crt_usr) or chgd
        
        return chgd
    
    def _frst_strt_tsk(self, tsks):
        ''' 并非所有任务都开始了 '''
        dt = tsk = None
        for t in tsks:
            if t.stg.dev_srt_tim and \
                (not dt or t.stg.dev_srt_tim < dt):
                dt = t.stg.dev_srt_tim
                tsk = t
        return tsk

    def _stt_4(self, stg, tsks, chgd):
        # dev_srt_tim / 开发开始时间(第一次) 
        #   / 第一个开始的任务
        tsk = self._frst_strt_tsk(tsks)
        if tsk:
            chgd = _sign_if_ne(stg, 'dev_srt_tim', tsk.stg.dev_srt_tim) or chgd
        return chgd
    
    def _stt_5(self, stg, tsks, chgd):
        # last dev end time
        tsk = sorted(tsks, key=lambda tsk:tsk.stg.dev_end_tim)[-1]
        # dev_end_tim / 开发完成时间|待测试(最后一次) 
        #   / 最后一个完成开发的任务
        chgd = _sign_if_ne(stg, 'dev_end_tim', tsk.stg.dev_end_tim) or chgd
        # dev_usr / 开发人员 
        #   / 人员
        chgd = _sign_if_ne(stg, 'dev_usr', tsk.stg.dev_usr) or chgd
        # dev_dur_est / 开发时长(预估)  
        #   / X
        dev_dur = Util.calc_work_dur(stg.dev_srt_tim, stg.dev_end_tim)
        # dev_dur / 总开发时长 
        #   / 含暂停
        chgd = _sign_if_ne(stg, 'dev_dur', dev_dur) or chgd
        # psd_srt_tim / 暂停开始时间(第一次)
        # psd_end_tim / 暂停结束时间(最后一次)
        # psd_usr / 暂停人员
        # psd_dur / 总暂停时长
        #   / X 任务之间的暂停，相互交错，无法统计出需求的总暂停时长来。
        # tst_srt_tim / 测试开始时间(第一次) 
        #   / 开发完成 : 测试开始
        chgd = _sign_if_ne(stg, 'tst_srt_tim', stg.dev_end_tim) or chgd
        return chgd
    
    def _stt_6(self, stg, tsks, chgd):
        for tsk in tsks:
            if not tsk.stg.tst_end_tim:
                # task 没测试，stroy 直接验收了。
                # 所以无法统计 测试相关时间 及
                # 无法设定验收开始时间。
                return chgd
            
        # last test end time
        tsk = sorted(tsks, key=lambda tsk:tsk.stg.tst_end_tim)[-1]
        # tst_end_tim / 测试完成时间|待验收(最后一次) 
        #   / 最后一个测试完成时间
        chgd = _sign_if_ne(stg, 'tst_end_tim', tsk.stg.tst_end_tim) or chgd
        # tst_usr / 测试人员 
        #   / 测试人员
        chgd = _sign_if_ne(stg, 'tst_usr', tsk.stg.tst_usr) or chgd
        # tst_dur_est / 测试时长(预估) 
        #   / X
        # tst_dur / 总测试时长 
        #   / 完成 - 开始
        tst_dur = Util.calc_work_dur(stg.tst_srt_tim, stg.tst_end_tim)
        chgd = _sign_if_ne(stg, 'tst_dur', tst_dur) or chgd

        # acc_srt_tim / 验收(acceptance)开始时间(第一次) 
        #   / 假设测试完就开始验收
        chgd = _sign_if_ne(stg, 'acc_srt_tim', stg.tst_end_tim) or chgd
        return chgd
    

    def _stt_7(self, stg, chgd):
        if not stg.acc_srt_tim:
            # 没有开始时间，无法统计耗时。
            return chgd
        
        # acc_end_tim / 验收完成时间|待发布(最后一次) 
        #   / 已有
        # acc_usr / 验收人员 
        #   / 已有
        # acc_dur / 总验收时长 
        #   / 完成 - 开始
        acc_dur = Util.calc_work_dur(stg.acc_srt_tim, stg.acc_end_tim)
        chgd = _sign_if_ne(stg, 'acc_dur', acc_dur) or chgd
        return chgd

    def _stt_8(self, chgd):
        # pub_tim / 发布时间|待结束 
        #   / X
        # pub_usr / 发布人员 
        #   / X
        return chgd
    
    STT_IDX = ['-XJ','-PS','AP-','-AP','KF-','CS-','-CS','-YS','-FB','-GB',]
              #   0 ,  1  ,  2  ,  3  ,  4  ,  5  ,  6  ,  7  ,  8  ,  9

    def _stry_task(self, stry):
        if hasattr(stry, '_has_Ts'):
            tasks = getattr(stry, '_has_Ts')
        else:
            tasks = load_children([stry], 'CN', typ='T')
        return tasks
    
    def calc_sty_stg(self, stry:Artifact):
        if stry.stt == '-QX': return False

        stg, chgd = ArtStage.objects.get_or_create(art=stry)
        if not stg: return False
        
        while True:
            si = self.STT_IDX.index(stry.stt)

            # 0. -XJ  >>> # 创建完
            chgd = self._stt_0(stg, stry, chgd)
            if si < 1: break
            # 1. -PS  >>>
            # 2. AP-  >>> # 评审完
            chgd = self._stt_2(stg, stry, chgd)
            if si < 3: break
            
            tasks = self._stry_task(stry)
            if not tasks: break

            # 3. -AP  >>> # 安排完
            chgd = _calc_sty_pnt(stry, tasks, chgd)
            chgd = self._stt_3(stg, tasks, chgd)
            if si < 4: break
            # 4. KF-  >>> # 开发中
            chgd = self._stt_4(stg, tasks, chgd)
            if si < 5: break 
            # 5. CS-  >>> # 开发完
            chgd = self._stt_5(stg, tasks, chgd)
            if si < 6: break 
            # 6. -CS  >>> # 测试完
            chgd = self._stt_6(stg, tasks, chgd)
            if si < 7: break

            # 7. -YS  >>> # 验收完
            chgd = self._stt_7(stg, chgd)
            # 8. -FB  >>>
            # 9. -GB  >>>

            break

        if chgd:
            stg.save()
            return Print.log(f'{stry} stg_calc~')

        return Print.dot()


    def calc_sty_stgs(self):
        Print.log('Calc sty stgs...')
        stys = Artifact.objects.filter(typ='S').all()
        for sty in stys:
            self.calc_sty_stg(sty)
        Print.log('Done.')

    TASK_STT = [
        ('-QX', '-AP'), #[0]
        ('KF-', 'KFX', '-KF', '-GB'), #[1] doing +
        ('-KF', '-GB'), #[2] testing +
        ('-GB',), #[3] tested
        ]
    
    def calc_perfs(self):
        Print.log('Calc sty/tsk perfs...')
        tsks = Artifact.objects.filter(typ='T').all()
        for tsk in tsks:
            if tsk.stt in self.TASK_STT[0]: continue
            self.calc_perf(tsk)
        Print.log('Done.')

    def get_perf(self, usr, typ, tim):
        if not usr: return None
        if not tim: return None
        perf, _ = Perf.objects.get_or_create(usr=usr, typ=typ, tim=tim)
        return perf

    def calc_perf(self, tsk):
        rls = Relation.objects.filter(art_b=tsk, rlt='CN', art_a__typ='S').all()
        sty = rls[0].art_a if len(rls) > 0 else None
        s_chgd = False

        if sty:
            if sty.stt == '-QX': return False

            dev_tim = sty.stg.dev_end_tim
            perf = self.get_perf(sty.stg.dev_usr, 'PK', dev_tim)
            if perf:
                rev_to_dev = Util.calc_work_dur(sty.stg.rev_end_tim, dev_tim)
                perf.dur = rev_to_dev
                perf.save()
                s_chgd = True

            if sty.stt in ('-YS', '-FB', '-GB'):
                tst_tim = sty.stg.tst_end_tim
                perf = self.get_perf(sty.stg.tst_usr, 'PC', tst_tim)
                if perf:
                    rev_to_tst = Util.calc_work_dur(sty.stg.rev_end_tim, tst_tim)
                    perf.dur = rev_to_tst
                    perf.spd = sty.pts() / (rev_to_tst.total_seconds()/8)
                    perf.save()
                    s_chgd = True

                acc_tim = sty.stg.acc_end_tim
                perf = self.get_perf(sty.stg.acc_usr, 'PY', acc_tim)
                if perf:
                    rev_to_acc = Util.calc_work_dur(sty.stg.rev_end_tim, acc_tim)
                    perf.dur = rev_to_acc
                    perf.spd = sty.pts() / (rev_to_acc.total_seconds()/8)
                    perf.save()
                    s_chgd = True


        pts = tsk.pts()
        t_chgd = False
        if tsk.stt in self.TASK_STT[2]:
            start_tst_dt = tsk.stg.tst_srt_tim
            dev_to_tst = Util.calc_work_dur(tsk.stg.dev_end_tim, start_tst_dt)
            perf = self.get_perf(tsk.stg.tst_usr,'KC',start_tst_dt)
            if perf:
                perf.dur = dev_to_tst
                perf.save()
                t_chgd = True
            
            if pts:
                perf = self.get_perf(tsk.stg.dev_usr, 'K', tsk.stg.dev_end_tim)
                if perf:
                    days = tsk.stg.dev_dur.total_seconds()/8
                    perf.spd = pts / days
                    perf.save()
                    t_chgd = True

        if tsk.stt in self.TASK_STT[3]:
            acc_end = tsk.stg.acc_end_tim
            tst_to_acc = Util.calc_work_dur(tsk.stg.tst_end_tim, acc_end)
            perf = self.get_perf(tsk.stg.acc_usr,'CY', acc_end)
            if perf:
                perf.dur = tst_to_acc
                perf.save()
                t_chgd = True

            if pts:
                perf = self.get_perf(tsk.stg.tst_usr, 'C', tsk.stg.tst_end_tim)
                if perf:
                    days = tsk.stg.tst_dur.total_seconds()/8
                    perf.spd = pts / days
                    perf.save()
                    t_chgd = True
        
        log = ''
        if t_chgd: log += f'{tsk} prf~'
        if s_chgd: log += f'{sty} prf~'
        if log: return Print.log(log)
        return Print.dot()
        


    def calc_itor_tim(self):
        ''' move last cls_tim to next ver crt_tim'''

        Print.log('Reset itor cls_tim ...')
        its = Artifact.objects.filter(typ='It').all()
        its_by_uid = {}
        for it in its:
            if it.cls_tim < datetime(year=2023, month=1, day=1):
                it.delete()
                it.save()
                continue
            if it.uid not in its_by_uid:
                its_by_uid[it.uid] = []
            its_by_uid[it.uid].append(it)

        one_day = timedelta(days=1)
        for its in its_by_uid.values():
            its.sort(key=lambda it:it.ver)
            for idx in range(len(its)-1):
                it = its[idx]
                nxt = its[idx+1]
                end_tim = nxt.crt_tim - one_day
                if it.cls_tim.date() != end_tim.date():
                    end_tim_str= end_tim.strftime('%Y-%m-%d 23:59:59')
                    it.cls_tim = datetime.strptime(end_tim_str, '%Y-%m-%d %H:%M:%S')
                    it.save()
                    Print.log(f'{it} itor_tim~')
                else:
                    Print.dot()

        Print.log('Done.')            





'''
from fkb.tools.calc_data import CalcData
cd = CalcData()
cd.calc_itor_tim()

from fkb.tools.calc_data import CalcData
cd = CalcData()
cd.calc_stys()

'''
