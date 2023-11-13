from datetime import date
import json

import MySQLdb
from django.db.models import Q

from fkb.models import *
from fkb.tools.util import Util
from fkb.tools.proc_table import ProcTable


class SyncDb:

    def proc_db_tbl(self, pt:ProcTable):
        print(f'Start sync {pt.ID_TYPE} ...')
        self.pt = pt
        setattr(self.pt, 'query', self.query)
        while not self._sync_db_done():
            ...
        print('Done.')

    def _load_db_sync_info(self)->Any:
        con_str = Config.get('db_connect')
        if con_str is None:
            print('db_connect not set in Config')
            return None, None

        try:
            con = json.loads(con_str)
            db = MySQLdb.connect(**con)        
            cur = db.cursor()
            return db, cur
        except:
            return None, None

    def _row_to_dict(self, 
                     row:Any, 
                     key_map:dict[str, str])->dict[str, Any]:
        db_dct = {}
        for idx, to_key in enumerate(key_map.values()):
            val = get_val(row[idx])
            db_dct[to_key] = val
        
        return db_dct

    def _sync_db_done(self):
        result = []
        dct = None

        try:
            result = self.pt.query_db()
            for row in result:
                dct = self._row_to_dict(row, self.pt.KEY_MAP)
                self.pt.change_dict(dct)
                self._save_dict(dct)

            self.pt.query_offset += len(result)

        except Exception as e:
            print(f'ERROR: {type(e)}{e}. FOR: \n {dct}')
            return True
        
        return len(result) < self.pt.LIMIT_ONCE

    def _save_dict(self, dct:dict[str,Any]):
        if self.pt.DB_TYPE == 'User':
            self._save_user(dct)
        elif self.pt.DB_TYPE == 'Artifact':
            self._save_artifact(dct)
        return None

    def _save_user(self, dct:dict[str,Any]):
        if 'act' not in dct or not dct['act']:
            return
        
        pkvs = User.make_pkeys(**dct)
        obj, _ = User.objects.get_or_create(**pkvs)
        changed = self._set_new_attr(obj, dct)

        if changed: 
            obj.save()
            print(f'updated:{obj}')

    def _save_artifact(self, dct:dict[str,Any]):
        if 'uid' not in dct or not dct['uid']:
            return

        dct['typ'] = self.pt.ID_TYPE
        pkvs = Artifact.make_pkeys(**dct)
        obj, _ = Artifact.objects.get_or_create(**pkvs)

        dct_rlt = Util.pop_key(dct, 'rlt')
        dct_stg = Util.pop_key(dct, 'stg')
        info_chgd = self._set_new_attr(obj, dct)

        log = f'update {obj} '
        if info_chgd:
            log += '~inf'

        if is_some(dct_stg):
            if self._set_stage(obj, dct_stg):
                log += ' ~stg'
                info_chgd = True

        if info_chgd:
            obj.save()

        rlt_chgd = False
        if is_some(dct_rlt):
            rlt_chgd = self._set_relate(obj, dct_rlt)
            if rlt_chgd:
                log += ' ~rlt'
                rlt_chgd = True

        if info_chgd or rlt_chgd:
            print(log)

    def _set_new_attr(self, obj:Artifact, dct:dict[str,Any]):
        changed = False
        diff = self._get_diff_attr(obj, dct)
        if len(diff) > 0:
            if self._set_obj_changed(obj, dct, diff):
                changed = True
        return changed


    def _get_obj_ab(self, this_obj:Any, re:dict[str, Any], art_a:bool):
        key = 'art_a' if art_a else 'art_b'
        if key not in re:return None
        kvs = re[key]
        if kvs == 'this': return this_obj

        if isinstance(kvs, dict):
            pkvs = Artifact.make_pkeys(**kvs)
            obj_ab, _ = Artifact.objects.get_or_create(**pkvs)
            return obj_ab
        
        return None

    def _get_rel_ab(self, obj:Any, re:dict[str, Any]):
        ''' if id is 0/''/None, returns None '''
        obj_a = self._get_obj_ab(obj, re, True)
        if obj_a is None: return None, False
        obj_b = self._get_obj_ab(obj, re, False)
        if obj_b is None: return None, False
        
        rel, new_ent = Relation.objects.get_or_create(
            art_a=obj_a, 
            rlt=re['rlt'], 
            art_b=obj_b)
        
        re_rdr = re['rdr'] if 'rdr' in re else None
        if rel.rdr != re_rdr:
            rel.rdr = re_rdr
            rel.save()
            return rel, True
    
        return rel, new_ent

    def _get_valid_rel(self, rel):
        try:
            arta = rel.art_a
            artb = rel.art_b
        except:
            return None
        
        return rel

    def _set_relate(self, obj:Artifact, new_rls:list[dict[str,Any]]):
        old_rls_chgd = set()
        rlt_changed = False

        rlts = Relation.objects.filter(Q(art_a=obj)|Q(art_b=obj)).all()
        if len(rlts) > 0:
            for rel in rlts:
                rel = self._get_valid_rel(rel)
                if rel is None: 
                    old_rls_chgd.add(rel)
                    continue

                if self.pt.relation_incharge(obj, rel):
                    old_rls_chgd.add(rel)

        rdr_changed = False
        for re in new_rls:
            rel, rdr_chgd = self._get_rel_ab(obj, re)
            if rel is None: continue
            if rdr_chgd: rdr_changed = True
            
            if rel in old_rls_chgd:
                # not changed, remove from obj_rls.
                old_rls_chgd.remove(rel)
            else:
                # new relation added to db.
                rlt_changed = True

        # remains in obj_rls are to be deleted.
        for rel in old_rls_chgd:
            rel.delete()
            rlt_changed = True
        
        return rlt_changed or rdr_changed

    def _set_stage(self, obj:Artifact, stg:dict[str,Any]):
        changed = False
        is_new = False
        if obj.stg is None:
            pkvs= ArtStage.make_pkeys(art=obj)
            nstg, is_new = ArtStage.objects.get_or_create(**pkvs)
            obj.stg = nstg

        diff = None if is_new else self._get_diff_attr(obj.stg, stg)
        if is_new or len(diff) > 0:
            real_chgd = self._set_obj_changed(obj.stg, stg, diff)
            if real_chgd:
                obj.stg.save()
                changed = True

        return changed
    
    def _get_db_mod(self, cls_typ:Any, pkv:dict[str,Any]):
        dc = cls_typ.objects.filter(**pkv)
        if len(dc) == 0:
            return None
        return dc[0]
    
    def _v2_date_if_v_date(self, v:Any, v2:Any):
        if v2 is None: return None
        if not isinstance(v, date):
            return v2
        if not isinstance(v, datetime):
            return v2.date()
        return v2

    def _get_diff_attr(self, obj1:Any, dct:dict[str,Any])->list[Any]:
        ''' without stg & rlt '''
        diff:list[Any] = []
        for k, v in dct.items():
            if hasattr(obj1, k):
                old_v = get_val(getattr(obj1, k))
                old_v = self._v2_date_if_v_date(v, old_v)
                if old_v != v:
                    diff.append(k)
        return diff
    
    def _set_obj_changed(self, obj:Any, kvs:dict[str, Any], diff:list[str]|None):
        really_changed = False

        dct = kvs.keys() if diff is None else diff
        for k in dct:
            old_v = getattr(obj, k)
            v = kvs[k]

            if isinstance(v, dict) and 'act' in v:
                v = self._get_db_mod(User, v)
            else:
                old_v = self._v2_date_if_v_date(v, old_v)
            
            if old_v != v:
                setattr(obj, k, v)
                really_changed = True

        return really_changed
    
    def __init__(self) -> None:
        self.db = None
        self.query = None
        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        if self.db is not None:
            return True
        self.db, self.query = self._load_db_sync_info()
        if self.db is None:
            return False

    def disconnect(self):
        if self.db is not None:
            self.db.close()
            self.db = None
            self.query = None