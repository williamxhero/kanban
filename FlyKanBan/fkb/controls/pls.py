
from fkb.controls.util import *


def get_data(pd_id:int, ongoing:str, **kvargs):
    if pd_id <= 0: return None
    stt = 'KF-' if ongoing == 'ongoing' else None

    kvs = {'typ':'Pd'}
    if stt: kvs['stt'] = stt
    kvs['uid'] = pd_id

    pds = Artifact.objects.filter(**kvs).all()
    if len(pds) == 0: return None

    pd_lst = [pds[0]]
    cur_pd = pd_lst[0]

    chn = load_children(pd_lst, 'CN', **kvs)
    pd_lst += chn
    
    kvs_pl = {'typ':'Pl', 'stt':stt}
    pls = load_children(pd_lst, 'CN',  **kvs_pl)

    kvs_it = {'typ':'It', 'stt':stt}
    load_children(pls, 'CN',  **kvs_it)

    for pd in pd_lst:
        pls_has_it = False
        if hasattr(pd, 'has_Pls'):
            for pl in pd.has_Pls:
                if hasattr(pl, 'has_Its') and len(pl.has_Its) > 0:
                    pls_has_it = True
                    break
        pd.pls_has_it = pls_has_it
    
    return {'pds':pd_lst,
            'cur_pd':cur_pd,
            'ongoing': ongoing, 
            }