from fkb.controls.util import *


def get_data(pl_id:int, ongoing:str, **kvargs):
    if pl_id <= 0: return None

    stt = 'KF-' if ongoing == 'ongoing' else None

    kvs = {'typ':'Pl', 'stt':stt, 'uid':pl_id,}
    pls = Artifact.objects.filter(**kvs).all()
    if len(pls) == 0: return None

    pl_lst = [pls[0]]
    cur_pl = pl_lst[0]

    kvs_pl = {'typ':'Pl', 'stt':stt}
    chn = load_children(pl_lst, 'CN', **kvs_pl)
    pl_lst += chn
    
    kvs_it = {'typ':'It', 'stt':stt}
    load_children(pl_lst, 'CN',  **kvs_it)

    kvs_pd = {'typ':'Pd', 'stt':stt}
    load_parents(pl_lst, 'CN', **kvs_pd)
    
    return {'pls':pl_lst,
            'cur_pl':cur_pl,
            'ongoing': ongoing, 
            }