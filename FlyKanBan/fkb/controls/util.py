from typing import Iterable
from fkb.models import *

def _same_from_collection(obj:object, 
                          objs:Iterable[Any])->Any:
    for o in objs:
        if o == obj:
            return o
    return obj

def last_version(art:Artifact):
    last_ver_art = Artifact.objects.filter(
        typ=art.typ, uid=art.uid).order_by('-ver').first()
    if last_ver_art is None: return art
    art_dct = art.__dict__
    for k, v in art_dct.items():
        if getattr(last_ver_art, k) is None:
            setattr(last_ver_art, k, v)
    return last_ver_art


def _get_typ_stt(**kwargs):
    if 'typ' not in kwargs: return None, None
    typ = kwargs['typ']
    if isinstance(typ, str):
        typ = [typ]

    stt = kwargs['stt'] if 'stt' in kwargs else None

    return typ, stt

def _a_append_has_b(rl, art_a, art_b):
    has_key = f'has_{rl.art_b.typ}s'
    attr = getattr(art_a, has_key, [])
    attr.append(art_b)
    setattr(art_a, has_key, attr)


def load_parents(art_b_lst:Iterable[Any], rlt, **a_kvargs):
    a_typ, a_stt = _get_typ_stt(**a_kvargs)
    if not a_typ: return []

    parents = []
    rls = Relation.objects.filter(art_b__in=art_b_lst, rlt=rlt, art_a__typ__in=a_typ).all()
    for rl in rls:
        if is_some(a_stt) and rl.art_a.stt != a_stt: continue
        art_b = _same_from_collection(rl.art_b, art_b_lst)
        art_a = _same_from_collection(rl.art_a, art_b_lst)
        setattr(art_b, f'of_{rl.art_a.typ}', art_a)
        _a_append_has_b(rl, art_a, art_b)
        parents.append(art_a)

    return parents


def load_children(art_as:Iterable[Artifact], rlt, **b_kvargs)->list[Artifact]:
    ''' children will have a new attribute `of_<a.typ>`  

    parents will have a new attribute `has_<b.typ>s`
    '''
    b_typ, b_stt = _get_typ_stt(**b_kvargs)
    if not b_typ: return []

    children = []
    rls = Relation.objects.filter(art_a__in=art_as, rlt=rlt, art_b__typ__in=b_typ).all()
    for rl in rls:
        if is_some(b_stt): 
            art_b = last_version(rl.art_b)
            if art_b.stt != b_stt:
                continue
        art_a = _same_from_collection(rl.art_a, art_as)
        art_b = _same_from_collection(rl.art_b, art_as)
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
        job = scd.add_job(run, 'cron', day_of_week='mon-fri', hour=6, minute=0)
    else:
        job = jobs[0]
    
    if not std:
        scd.start()
        std = True

    return job.next_run_time
