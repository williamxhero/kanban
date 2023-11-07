
from fkb.controls.util import *

def get_data(ongoing:str, **kvargs):
    kvs = {'typ':'Pd'}
    stt = 'KF-' if ongoing == 'ongoing' else None
    if stt:
        kvs['stt'] = 'KF-'


    pds = Artifact.objects.filter(**kvs).all()
    pds_dct = {pd:True for pd in pds}

    chn = load_children(pds_dct.keys(), 'CN', **kvs)
    for pd in chn:
        pds_dct[pd] = True

    kvs_pls = {'typ':'Pl', 'stt':stt}
    all_pds = list(pds_dct.keys())
    load_children(all_pds, 'CN', **kvs_pls)

    return {'pds':all_pds, 
            'ongoing': ongoing}