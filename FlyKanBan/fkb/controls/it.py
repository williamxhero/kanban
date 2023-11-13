from fkb.controls.util import *

def _sts_into_its(it_sts, sts):
    its_sts = {it:[] for it in it_sts}
    lst_it = it_sts[0]
    fst_it = it_sts[-1]

    for st in sts:
        st_rev_time = st.stg.rev_end_tim
        if st_rev_time is None:
            # 没评审，过
            continue

        st_acc_time = st.stg.acc_end_tim
        if st_acc_time is None:
            # 没验收，最后一个迭代
            its_sts[lst_it].append(st)
            continue
        
        # 按验收时间，归类到相应迭代
        found = False
        for it in it_sts:
            if st_acc_time >= it.crt_tim:
                its_sts[it].append(st)
                found = True
                break
        
        # 没找到，归类到第一个迭代
        if not found:
            its_sts[fst_it].append(st)
    
    return its_sts

def get_data(it_id:int, **kvargs):
    its_q = Artifact.objects.filter(typ='It', uid=it_id).order_by('-ver').all()
    if len(its_q) == 0: return None
    its = list(its_q)
    id_it = its[-1] # ver 0 itor for reference.
    last_it = its[0]
    
    all_its = [id_it]
    all_its += load_children(all_its, 'CN', typ='It')

    sttks = load_children(all_its, 'CN', typ=['S', 'T'])
    it_sts = _sts_into_its(its, sttks)

    return {
        'id_it':id_it,
        'last_it':last_it,
        'its':it_sts,
        }
