from typing import Iterable
from fkb.models import *

def _same_from_collection(obj:object, 
                          objs:Iterable[Any])->Any:
    for o in objs:
        if o == obj:
            return o
    return obj

def frst_version(art:Artifact):
    if art.ver == 0: return art
    art_v0 = Artifact.objects.filter(
        typ=art.typ, uid=art.uid).order_by('ver').first()
    return art_v0 if art_v0 else art

def last_version(art:Artifact):
    lv = Artifact.objects.filter(
        typ=art.typ, uid=art.uid).order_by('-ver').first()
    if lv is None: return art
    art_dct = art.__dict__
    for k, v in art_dct.items():
        if not hasattr(lv, k) or getattr(lv, k) is None:
            setattr(lv, k, v)
    return lv


def _get_typ_stt(**kwargs):
    if 'typ' not in kwargs: return None, None, None
    typ = kwargs['typ']
    if isinstance(typ, str):
        typ = (typ,)

    stts = kwargs['stts'] if 'stts' in kwargs else None
    if stts and isinstance(stts, str):
        stts = (stts,)

    no_stts = kwargs['no_stts'] if 'no_stts' in kwargs else None
    if no_stts and isinstance(no_stts, str):
        no_stts = (no_stts,)

    return typ, stts, no_stts

def _a_append_has_b(rl, art_a, art_b):
    has_key = f'has_{rl.art_b.typ}s'
    attr = getattr(art_a, has_key, [])
    attr.append(art_b)
    setattr(art_a, has_key, attr)


def load_parents(art_bs:Iterable[Any], rlt, **a_kvargs):
    ''' children will have a new attribute `of_<a.typ>`  
    parents will have a new attribute `has_<b.typ>s`
    both children and parents will refer to ver0.

    param:
        typ: what typ arts you want to load? str or tuple[str]
        stts: what status do you want? str or tuple[str]
        no_stts: what status you don't want?  str or tuple[str]
    '''
    a_typ, a_stts, no_a_stts = _get_typ_stt(**a_kvargs)
    if not a_typ: return []

    parents = []
    art_b0s = [frst_version(art_b) for art_b in art_bs]
    rls = Relation.objects.filter(art_b__in=art_b0s, rlt=rlt, art_a__typ__in=a_typ).all()
    for rl in rls:
        if is_some(no_a_stts) and rl.art_a.stt in no_a_stts: continue
        if is_some(a_stts) and rl.art_a.stt not in a_stts: continue
        art_b = _same_from_collection(rl.art_b, art_b0s)
        art_a = _same_from_collection(rl.art_a, art_b0s)
        setattr(art_b, f'of_{rl.art_a.typ}', art_a)
        _a_append_has_b(rl, art_a, art_b)
        parents.append(art_a)

    return parents


def load_children(art_as:Iterable[Artifact], rlt, **b_kvargs)->list[Artifact]:
    ''' children will have a new attribute `of_<a.typ>`  
    parents will have a new attribute `has_<b.typ>s`
    both children and parents will refer to ver0.

    param:
        typ: what typ arts you want to load? str or tuple[str]
        stts: what status do you want? str or tuple[str]
        no_stts: what status you don't want?  str or tuple[str]

    '''
    b_typ, b_stts, no_b_stts = _get_typ_stt(**b_kvargs)
    if not b_typ: return []

    children = []
    art_a0s = [frst_version(art_a) for art_a in art_as]
    rls = Relation.objects.filter(art_a__in=art_a0s, rlt=rlt, art_b__typ__in=b_typ).all()
    for rl in rls:
        art_b = last_version(rl.art_b)
        if is_some(no_b_stts) and art_b.stt in no_b_stts: continue
        if is_some(b_stts) and art_b.stt not in b_stts: continue
        art_a = _same_from_collection(rl.art_a, art_a0s)
        art_b = _same_from_collection(rl.art_b, art_a0s)
        setattr(art_b, f'of_{art_a.typ}', art_a)
        _a_append_has_b(rl, art_a, art_b)
        children.append(art_b)

    return children


from apscheduler.schedulers.background import BackgroundScheduler
scd = BackgroundScheduler()
std = False # started

def run():
    from fkb.tools.proc_table_flyzt import PTFZT
    p = PTFZT()
    p.sync_all()


def run_scheduler():
    global std, scd
    jobs = scd.get_jobs()

    if len(jobs) == 0:
        if not run: return None
        job = scd.add_job(run, 'cron', hour=3, minute=0)
    else:
        job = jobs[0]
        
    if not std:
        try:
            scd.start()
        finally:
            std = True

    return job.next_run_time
    
