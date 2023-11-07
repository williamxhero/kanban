from datetime import date
import json

import MySQLdb
from django.db.models import Q

from fkb.models import *
from fkb.tools.util import Util
from fkb.tools.proc_table import ProcTable


class SyncDb:

    def proc_db_tbl(self, pt:ProcTable):
        self.pt = pt
        while not self._sync_db_done():
            ...

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
            result = self.pt.query_db(self.query)
            for row in result:
                dct = self._row_to_dict(row, self.pt.KEY_MAP)
                self.pt.change_dict(dct)
                self._save_dict(dct)

            self.pt.query_offset += len(result)

        except Exception as e:
            print(f'{e}: {dct}')
            return True
        
        return len(result) < self.pt.LIMIT_ONCE

    def _save_dict(self, dct:dict[str,Any]):
        if self.pt.DB_TYPE == 'User':
            self._save_user(dct)
        elif self.pt.DB_TYPE == 'Artifact':
            self._save_artifact(dct)
        return None

    def _save_user(self, dct:dict[str,Any]):
        pkvs = User.make_pkeys(**dct)
        obj, _ = User.objects.get_or_create(**pkvs)
        changed = self._set_new_attr(obj, dct)

        if changed: 
            obj.save()
            print(f'updated:{obj}')

    def _save_artifact(self, dct:dict[str,Any]):
        dct['typ'] = self.pt.ID_TYPE
        pkvs = Artifact.make_pkeys(**dct)
        obj, _ = Artifact.objects.get_or_create(**pkvs)

        dct_rlt = Util.pop_key(dct, 'rlt')
        dct_stg = Util.pop_key(dct, 'stg')
        changed = self._set_new_attr(obj, dct)
        
        if is_some(dct_stg):
            if self._set_stage(obj, dct_stg):
                print(f'updated:{obj} stg')

        if is_some(dct_rlt):
            if self._set_relate(obj, dct_rlt):
                print(f'updated:{obj} rlt')

        if changed:
            obj.save()
            print(f'updated:{obj}')

    def _set_new_attr(self, obj:Artifact, dct:dict[str,Any]):
        changed = False
        diff = self._get_diff_attr(obj, dct)
        if len(diff) > 0:
            if self._set_obj_changed(obj, dct, diff):
                changed = True
        return changed


    def _get_rel_arb(self, obj:Any, re:dict[str, Any]):
        ''' if id is 0/''/None, returns None '''
        kvs_a = re['art_a'] if 'art_a' in re else None
        kvs_b = re['art_b'] if 'art_b' in re else None

        obj_a = None
        obj_b = None

        if isinstance(kvs_a, dict):
            pkvs = Artifact.make_pkeys(**kvs_a)
            obj_a, _ = Artifact.objects.get_or_create(**pkvs)

        if isinstance(kvs_b, dict):
            pkvs = Artifact.make_pkeys(**kvs_b)
            obj_b, _ = Artifact.objects.get_or_create(**pkvs)

        if kvs_a == 'this':
            obj_a = obj

        if kvs_b == 'this':
            obj_b = obj

        if obj_a is None or obj_b is None:
            return None
        
        rel, _ = Relation.objects.get_or_create(
            art_a=obj_a, 
            rlt=re['rlt'], 
            art_b=obj_b)
        
        return rel

    def _set_relate(self, obj:Artifact, obj_rlt:list[dict[str,Any]]):
        ''' obj_rlt 中只有：不同类父 和 同类子 两种关系'''
        obj_rls = {}
        changed = False

        rlts = Relation.objects.filter(Q(art_a=obj)|Q(art_b=obj)).all()
        if len(rlts) > 0:
            for rel in rlts:
                if rel.art_b == obj:
                    # obj的不同类父关系（ T/B->S->It->Pl->Pd )
                    if rel.art_a.typ != obj.typ:
                        obj_rls[str(rel)] = rel
                else: 
                    # obj的同类子关系
                    if obj.typ == rel.art_b.typ:
                        obj_rls[str(rel)] = rel

        for re in obj_rlt:
            rel = self._get_rel_arb(obj, re)
            if rel is None: continue

            rel_key = str(rel)
            if rel_key in obj_rls:
                # nothing.
                del obj_rls[rel_key]
            else:
                changed = True

        for rel in obj_rls.values():
            rel.delete()
            changed = True
        
        return changed

    def _set_stage(self, obj:Artifact, stg:dict[str,Any]):
        changed = False
        is_new = False
        if obj.stg is None:
            pkvs= ArtStage.make_pkeys(art=obj)
            nstg, is_new = ArtStage.objects.get_or_create(**pkvs)
            obj.stg = nstg

        diff = None if is_new else self._get_diff_attr(obj.stg, stg)
        if is_new or len(diff) > 0:
            self._set_obj_changed(obj.stg, stg, diff)
            obj.stg.save()

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