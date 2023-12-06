
from datetime import timedelta
from work_hours import WorkHours

from fkb.controls.util import *
from fkb.controls.util_wd import *
from fkb.controls.util_list import *


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
        pts = tsk.pts()

        if pts < 0:
            pts = 'n/a'
        elif pts == 0:
            pts = 0.1
        else:
            pts = pts
        setattr(tsk, 'pts', pts)

def _load_all_TSs(it0s):
    it0s += load_children(it0s, 'CN', typ='It')
    load_parents(it0s, 'CN', typ=('Pl', 'Pd'))
    STs = load_children(it0s, 'CN', typ=('S', 'T'))
    return STs

def _get_ST_cls_tim(ST):
    if ST.stt in ('KFX', 'KF-'):
        return None

    if ST.typ == 'S':
        end_tim = ST.stg.acc_end_tim
    else:
        end_tim = ST.stg.tst_end_tim

    if end_tim is None:
        end_tim = ST.cls_tim # canceled.

    return end_tim

def _get_ST_dev_usr(ST):
    if ST.stg.dev_usr: return ST.stg.dev_usr
    if ST.rsp_usr: return ST.rsp_usr
    if ST.cls_usr: return ST.cls_usr
    return None

    
TASK_ORDER=('KFX','KF-','-KF','-AP','-GB','-QX')

def _order_STs(STs):
    def get_stt_idx(ST):
        if ST.stt in TASK_ORDER:
            return TASK_ORDER.index(ST.stt)
        return 0
    
    return sorted(STs, key=get_stt_idx)

def _get_ongoing_it(it):
    if it.of_Pl.stt != 'KF-': return None
    if it.of_Pd.stt != 'KF-': return None
    it = last_version(it)
    if it.stt != 'KF-': return None
    return it

def _get_lst_STs(it0s, STs):
    if not it0s: return []
    itxs = set()
    sts = []
    for ST in STs:
        it = _get_ongoing_it(ST.of_It)
        if not it: continue
        end_tim = _get_ST_cls_tim(ST)
        if not end_tim or \
            it.crt_tim.date() <= end_tim.date() <= it.cls_tim.date():
            sts.append(ST)
            itxs.add(it)

    return list(itxs), _order_STs(sts)


def _get_uniqe_art(arts):
    ''' reutrn art if all arts are same else None '''
    if not arts: return None
    if len(set(arts)) > 1: return None
    return arts[0]

def _get_ppi(*rels_lst, pds=[], pls=[]):
    arts = list(pds)+list(pls)
    arts_has = {str(a):a for a in arts}

    ppi = {'Pd':{}, 'Pl':{}, 'It':{}}

    for rels in rels_lst:
        for rel in rels:
            art_b = rel.art_b
            typ_dct = ppi[art_b.typ]
            if art_b.uid in typ_dct:
                continue

            art_b = arts_has.get(str(art_b), art_b)
            art_b = typ_dct.setdefault(art_b.uid, art_b)

            art_a = arts_has.get(str(rel.art_a), rel.art_a)
            typ_dct = ppi[art_a.typ]
            art_a = typ_dct.setdefault(art_a.uid, art_a)

            setattr(art_b, f'of_{art_a.typ}', art_a)

    pds_dct, pls_dct, its_dct = ppi['Pd'], ppi['Pl'], ppi['It']
    pds, pls, its = list(pds_dct.values()), \
                     list(pls_dct.values()), list(its_dct.values())

    # set of_Pd for it
    for it in its:
        pl = it.of_Pl
        pd = pl.of_Pd
        setattr(it, 'of_Pd', pd)
    
    return pds, pls, its


def _get_all_art_b(rels):
    arts = {}
    for rel in rels:
        arts[rel.art_b.uid] = rel.art_b
    return list(arts.values())


def _calc_burn(its, STs):
    uid_tim = {it.uid:it.cls_tim for it in its}
    tdy_d = date.today()

    its.sort(key=lambda x:x.crt_tim)
    frst_start = its[0].crt_tim

    # 某日完成总点数
    frst_start_dt = frst_start.date()
    dt_fin_pts = {frst_start_dt:0}
    # 某日理想点数
    dt_idl_pts= {frst_start_dt:0}

    for st in STs:
        if st.typ == 'S':continue
        st_pts = st.pts if st.pts != 'n/a' else 0
        cls_tim = _get_ST_cls_tim(st)
        if cls_tim:
            cls_dt = cls_tim.date()
            pts = dt_fin_pts.get(cls_dt, 0)
            pts += st_pts
            dt_fin_pts[cls_dt] = pts

        it = _get_ongoing_it(st.of_It)
        if not it: continue

        it_cls_tim = uid_tim.get(it.uid, None)
        if not it_cls_tim: continue

        it_cls_dt = it_cls_tim.date()
        itpt = dt_idl_pts.get(it_cls_dt, 0)
        itpt += st_pts
        dt_idl_pts[it_cls_dt] = itpt

    idl_pts = dct_to_lst_sorted(dt_idl_pts)
    idl_pts = accumulate_val(idl_pts)
    idl_lst = fill_daily_interpolate(idl_pts)

    fin_pts = dct_to_lst_sorted(dt_fin_pts)    
    fin_pts.append((idl_lst[-1][0], 0))
    fin_pts = accumulate_val(fin_pts)
    fin_lst = fill_daily_previous(fin_pts)

    idl_fin = [(idl_lst[i][0], idl_lst[i][1], fin_lst[i][1]) for i in range(len(idl_lst))]
    
    # calc view start and end
    wh = WorkHours()
    tdy_dt = datetime(tdy_d.year, tdy_d.month, tdy_d.day, 0, 0, 0)
    its.sort(key=lambda x:x.cls_tim)
    frst_close = its[0].cls_tim

    s2t = calc_workdays(frst_start, tdy_dt)
    t2c = calc_workdays(tdy_dt, frst_close)
    
    if s2t == t2c:
        start = wh.add_workdays(tdy_dt, -5)
        end = wh.add_workdays(tdy_dt, 5)
    elif s2t < t2c:
        start = frst_start
        end = wh.add_workdays(start, 10)
    else:
        end = frst_close
        start = wh.add_workdays(end, -10)

    # 算出view的百分比
    e2s_dys = calc_workdays(frst_start, frst_close)
    start_pctg = 0
    end_pctg = 1

    if frst_start < start:
        start_pctg = calc_workdays(frst_start, start) / e2s_dys

    if frst_close > end:
        end_pctg = calc_workdays(end, frst_start) / e2s_dys

    return idl_fin, start_pctg, end_pctg


def _calc_hist(STs:list[Artifact]):
    wh = WorkHours()
    _1day = timedelta(days=1)

    dt_pts = {} # date / points
    dt_ppl = {} # date / people

    # 将点数平分累加到所有工作日
    Ts = [st for st in STs if st.typ == 'T']
    clsd_Ts = [t for t in Ts if is_some(t.stg.dev_srt_tim)]

    for t in clsd_Ts:
        cls_tim = _get_ST_cls_tim(t)
        if not cls_tim: continue
        stt_dt = t.stg.dev_srt_tim.date()
        end_dt = cls_tim.date()
        rsp_usr = _get_ST_dev_usr(t)

        wd_cnt = calc_workdays(stt_dt, end_dt)
        if wd_cnt == 0: wd_cnt = 1
        pts = t.pts if t.pts != 'n/a' else 0
        ppd = pts / wd_cnt # points per day

        while stt_dt <= end_dt:
            if wh.is_workday(stt_dt):
                dt_pts[stt_dt] = dt_pts.get(stt_dt, 0) + ppd

                ppl_set = dt_ppl.get(stt_dt, set())
                if rsp_usr:
                    ppl_set.add(rsp_usr)
                dt_ppl[stt_dt] = ppl_set

            stt_dt += _1day

    dt_ppl = {dt:len(st) for dt,st in dt_ppl.items()}

    pts = dct_to_lst_sorted(dt_pts)
    dts = [dp[0] for dp in pts]
    pts = [dp[1] for dp in pts]
    
    # 计算移动平均
    ave_day = 40
    ave = mov_ave(pts, ave_day)

    # people per day
    ppl = [dt_ppl[dt] for dt in dts]
    # points per person per day
    ppp = [dt_pts[dt]/dt_ppl[dt] for dt in dts]
    appp = mov_ave(ppp, 40)

    # 整体返回
    dt_pts = [dpa for dpa in zip(dts,pts,ave,ppp,appp,ppl)]
    return dt_pts, ave_day

def get_data(typ:str, ids:list[int], **kvargs):
    typ = typ.lower()

    if typ == 'pd':
        pds = Artifact.objects.filter(typ='Pd', uid__in=ids).all()
        rels_pp = Relation.objects.filter(art_a__in=pds, rlt='CN', art_b__typ='Pl').all()
        pls = _get_all_art_b(rels_pp)
        rels_pi = Relation.objects.filter(art_a__in=pls, rlt='CN', art_b__typ='It').all()
        pds, pls, it0s = _get_ppi(rels_pp, rels_pi, pds=pds, pls=pls)

    elif typ == 'pl':
        pls = Artifact.objects.filter(typ='Pl', uid__in=ids).all()
        rels_pp = Relation.objects.filter(art_a__typ='Pd', rlt='CN', art_b__in=pls).all()
        rels_pi = Relation.objects.filter(art_a__in=pls, rlt='CN', art_b__typ='It').all()
        pds, pls, it0s = _get_ppi(rels_pp, rels_pi, pls=pls)

    elif typ == 'it':
        rels = Relation.objects.filter(art_a__typ__in=['Pd', 'Pl'], rlt='CN',
                                       art_b__typ='It', art_b__in=ids).all()
        pds, pls, it0s = _get_ppi(rels)
    else:
        return None
    
    if len(it0s) == 0: return None

    all_STs = _load_all_TSs(it0s)
    _solid_pts(all_STs)

    # calc all history data.
    hist, ave_day = _calc_hist(all_STs)

    # calc last itor burn up data.
    its, STs = _get_lst_STs(it0s, all_STs)
    idl_fin, vst, ved = _calc_burn(its, STs)

    # set pd/pl info
    cur_pd = _get_uniqe_art([it.of_Pd for it in its])
    cur_pl = _get_uniqe_art([it.of_Pl for it in its])

    return {
        'cur_pd':cur_pd,
        'cur_pl':cur_pl,
        'cur_its':its,
        'cur_STs':STs,

        'burn_lst':idl_fin, # ideal burn down list
        'vse':(vst*100, ved*100),

        'hist':hist,
        'ave_day':ave_day,

        'next_sync':run_scheduler(),
        }
