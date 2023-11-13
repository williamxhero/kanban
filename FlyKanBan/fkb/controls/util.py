from typing import Iterable
from fkb.models import *

def _same_from_collection(obj:object, 
                          objs:Iterable[Any],
                          new_kvs:dict[str, Any]={})->Any:
    for o in objs:
        if o == obj:
            for k,v in new_kvs.items():
                if not hasattr(o, k):
                    setattr(o, k, v)
            return o
    return None

def _last_version(art:Artifact):
    last_ver_art = Artifact.objects.filter(
        typ=art.typ, uid=art.uid).order_by('-ver').first()
    if last_ver_art is None: return art
    art_dct = art.__dict__
    for k, v in art_dct.items():
        if getattr(last_ver_art, k) is None:
            setattr(last_ver_art, k, v)
    return last_ver_art


def load_parents(art_bs:Iterable[Any], rlt, **a_kvargs):
    if 'typ' not in a_kvargs: return
    a_typ = a_kvargs['typ']
    parent_key = f'of_{a_typ}'
    parents = []
    rls = Relation.objects.filter(art_b__in=art_bs, rlt=rlt).all()
    a_stt = a_kvargs['stt'] if 'stt' in a_kvargs else None
    for rl in rls:
        if rl.art_a.typ != a_typ: continue
        rl_art_a = _last_version(rl.art_a)
        if is_some(a_stt) and rl_art_a.stt != a_stt: continue
        art_b = _same_from_collection(rl.art_b, art_bs, {parent_key:True})
        art_a = _same_from_collection(rl_art_a, art_bs, {f'has_{art_b.typ}s':[]}) \
            if a_typ == art_b.typ else None
        if art_a is None:
            art_a = rl_art_a
        
        setattr(art_a, f'has_{art_b.typ}', art_b)
        setattr(art_b, parent_key, art_a)
        parents.append(art_a)

    return parents



def load_children(art_as:Iterable[Any], rlt, **b_kvargs)->list[Any]:
    ''' children will have a new attribute `of_<a.typ>`  

    parents will have a new attribute `has_<b.typ>s`
    '''
    if 'typ' not in b_kvargs: return
    b_typ = b_kvargs['typ']
    if isinstance(b_typ, str):
        b_typ = [b_typ]

    children = []
    rls = Relation.objects.filter(art_a__in=art_as, rlt=rlt).all()
    b_stt = b_kvargs['stt'] if 'stt' in b_kvargs else None
    for rl in rls:
        if rl.art_b.typ not in b_typ: continue
        children_key = f'has_{rl.art_b.typ}s'
        rl_art_b = _last_version(rl.art_b)
        if is_some(b_stt) and rl_art_b.stt != b_stt: continue
        art_a = _same_from_collection(rl.art_a, art_as, {children_key:[]})
        art_b = _same_from_collection(rl_art_b, art_as) \
            if art_a.typ in b_typ else None
        if art_b is None:
            art_b = rl_art_b

        setattr(art_b, f'of_{art_a.typ}', art_a)
        attr = getattr(art_a, children_key)
        attr.append(art_b)
        children.append(art_b)

    return children