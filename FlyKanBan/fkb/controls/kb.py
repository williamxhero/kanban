from datetime import timedelta
from fkb.tools.util import Util
from fkb.controls.util import *

def mov_ave(lst, window_size):
    aves = []
    
    for i in range(len(lst)):
        bef = max(0, i - window_size)
        sub_lst = lst[bef:i+1]
        ave = [sub_lst[-1][0],]
        for j in range(1, 5):
            js = [x[j] for x in sub_lst]
            s = sum(js)
            a = s / len(js)
            ave.append(a)
        aves.append(tuple(ave))
    return aves

TASK_ORDER=('KFX','KF-','-KF','-AP','-GB','-QX')

def _order_last_STs(its_STs, lst_it):
    STs = its_STs[lst_it]
    tsks = [tsk for tsk in STs if tsk.typ == 'T']
    tsks.sort(key=lambda t: TASK_ORDER.index(t.stt))
    its_STs[lst_it] = tsks

def _combine_its(its):
    ''' itor 的长度，最后一未结束 itor 中最短的 
    用itor的长度，重新划分第一个crt_tim 到 最后一个cls_tim 的时间段
    返回新的 itor 列表
    '''
    if len(its) == 0: return []
    if len(its) == 1: return its
    # find the un-closed itor:
    tdy_dt = date.today()
    unclosed = [it for it in its if it.cls_tim.date() >= tdy_dt]
    if len(unclosed) == 0:
        # cls_tim latest one:
        its.sort(key=lambda it: it.cls_tim)
        last = its[-1]
        hrs = Util.calc_work_dur(last.crt_tim, last.cls_tim)
    else:
        uncls_hrs = [Util.calc_work_dur(it.crt_tim, it.cls_tim) for it in unclosed]
        hrs = timedelta(days=10)
        for h in uncls_hrs:
            if h and h < hrs:
                hrs = h
    # find the minmal crt_tim and max cls_tim
    min_crt_tim = min([it.crt_tim for it in its])
    max_cls_tim = max([it.cls_tim for it in its])

    # split the time range by hrs
    itors = []
    itor = None
    idx = 0
    while min_crt_tim < max_cls_tim:
        itor = Artifact(typ='It',uid=0, ver=idx)
        itor.crt_tim = min_crt_tim
        itor.cls_tim = min_crt_tim + hrs
        itors.append(itor)
        min_crt_tim += hrs
        idx += 1

    return itors

def _ST_into_its(its, STs):

    its_STs = {it.uid:[] for it in its}
    lst_it = its[0]
    fst_it = its[-1]

    for ST in STs:
        isS = ST.typ == 'S'
        if isS and ST.stg.rev_end_tim is None:
            # 需求 没评审，过
            continue

        st_end_time = ST.stg.acc_end_tim if isS else ST.stg.tst_end_tim
        if st_end_time is None:
            st_end_time = ST.cls_tim
        
        if st_end_time is None:
            # 没验收，没测完，没关闭。最后一个迭代
            its_STs[lst_it].append(ST)
            continue
        
        # 按验收时间，归类到相应迭代
        found = False
        for it in its:
            if st_end_time >= it.crt_tim:
                its_STs[it].append(ST)
                found = True
                break
        
        # 没找到，归类到第一个迭代
        if not found:
            its_STs[fst_it].append(ST)
    
    return its_STs

def _calc_metrics(its_STs, its):
    it_mtcs = []
    it_ma = [] # moving average
    tdy_dt = date.today()
    year_ago = tdy_dt - timedelta(days=365)

    for it in its[-1:0:-1]:
        if it.cls_tim.date() < year_ago: continue
        it_ver = str(it.ver)
        it_pts_len = len(it_mtcs)
        STs = its_STs[it]
        tsks = [tsk for tsk in STs if tsk.typ == 'T']
        
        if len(tsks) == 0: 
            if it_pts_len > 0:
                it_mtcs.append((it_ver, 0, 0, 0, 0))
            continue

        ttl_pts = 0
        ppl = set()
        for tsk in tsks:
            if tsk.stt not in ('-GB', '-KF'): continue
            if tsk.rsp_usr.act != 'hw0':
                ppl.add(tsk.rsp_usr)
            if not tsk.pts: continue
            ttl_pts += tsk.pts
        
        ppl_cnt = len(ppl)
        if ppl_cnt == 0:
            if it_pts_len > 0:
                it_mtcs.append((it_ver, 0, 0, 0, 0))
            continue

        dur = Util.calc_work_dur(it.crt_tim, it.cls_tim)
        ttl_hrs = ppl_cnt * (dur.total_seconds()/3600)
        
        if ttl_hrs > 0 or it_pts_len > 0:
            it_mtcs.append((it_ver, 
                        ttl_pts, ttl_pts/ppl_cnt, 
                        ttl_hrs, ttl_pts/ttl_hrs,
                        ))
        
    it_ma = mov_ave(it_mtcs, 4)
    return it_mtcs, it_ma

def _calc_last_burn_up(its_STs, lst_it):
    # 迭代按版本排倒序
    pts_to_ystdy = {}
    it_ttl_pts = 0
    tdy_dt = date.today()

    STs = its_STs[lst_it]
    tsks = [tsk for tsk in STs if tsk.typ == 'T']

    for tsk in tsks:
        if tsk.stt == '-QX': continue

        it_ttl_pts += tsk.pts

        end_tim = tsk.stg.tst_end_tim
        if end_tim is None: continue
        end_dt = end_tim.date()
        if end_dt >= tdy_dt: continue

        pts = pts_to_ystdy.get(end_dt, 0)
        pts_to_ystdy[end_dt] = pts + tsk.pts

    dt_lst = []

    amt = 0
    dt = lst_it.crt_tim.date()
    while dt < tdy_dt:
        if dt in pts_to_ystdy:
            pts = pts_to_ystdy[dt]
            amt += pts
        dt_lst.append((dt, amt))
        dt += timedelta(days=1)

    return dt_lst, it_ttl_pts

def get_pdpl(it, pl=None):
    if is_some(it):
        pls_rls = Relation.objects.filter(art_b=it, rlt='CN').all()
        for pl_rls in pls_rls:
            setattr(it, 'of_Pl', pl_rls.art_a)
            pl = pl_rls.art_a
            break

    if is_some(pl):
        pds_rls = Relation.objects.filter(art_b=pl, rlt='CN').all()
        for pd_rls in pds_rls:
            setattr(pl, 'of_Pd', pd_rls.art_a)
            if it:
                setattr(it, 'of_Pd', pd_rls.art_a)

def _solid_pts(tsks):
    for tsk in tsks:
        setattr(tsk, 'pts', tsk.pts() or 0.1)

def get_data(typ:str, id:int, **kvargs):
    typ = typ.lower()

    if typ == 'pd':
        pd = Artifact.objects.filter(typ='Pd', uid=id).all()
        if len(pd) == 0: return None
        rels = Relation.objects.filter(art_a=pd[0], rlt='CN', art_b__typ='It').all()
        it_ids = [rl.art_b.uid for rl in rels if rl.art_b.stt != '-QX']

    elif typ == 'pl':
        pl = Artifact.objects.filter(typ='Pl', uid=id).all()
        if len(pl) == 0: return None
        rels = Relation.objects.filter(art_a=pl[0], rlt='CN', art_b__typ='It').all()
        it_ids = [rl.art_b.uid for rl in rels if rl.art_b.stt != '-QX']

    elif typ == 'it':
        it_ids=[id]
    else:
        return None
    
    its_q = Artifact.objects.filter(typ='It', uid__in=it_ids).order_by('-ver', '-cls_tim').all()
    if len(its_q) == 0: return None
    its = list(its_q)
    if len(its) == 0: return None

    
    all_its = [it for it in its if it.ver == 0]
    all_its += load_children(all_its, 'CN', typ='It')

    STs = load_children(all_its, 'CN', typ=['S', 'T'])
    its = _combine_its(its)
    its_STs = _ST_into_its(its, STs)

    its = list(its_STs.keys())
    id_it = its[-1] # ver 0.
    lst_it = its[0] # ver max.

    _solid_pts(STs)
    burn, total = _calc_last_burn_up(its_STs, lst_it)
    _order_last_STs(its_STs, lst_it)
    mtcs, ave_mtcs = _calc_metrics(its_STs, its)
    get_pdpl(it=id_it)

    no_data = len(mtcs) == 0

    return {
        'id_it':id_it,
        'last_it':lst_it,
        'its':its_STs,
        'chart':burn,
        'total':total,
        'mtcs':mtcs,
        'ave_mtcs':ave_mtcs,
        'mtcs_frt':0 if no_data else mtcs[0][0],
        'mtcs_lst':str(lst_it.ver),
        'next_sync':run_scheduler(),
        }
