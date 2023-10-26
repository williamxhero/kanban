import json

import MySQLdb
from FlyKanBan.fkb.controls.util import Util

from fkb.models import *
from fkb.controls.proc_table import ProcTable


class SyncDb:

    def _load_db_sync_info(self)->Any:
        con_str = Config.get('db_connect')
        if con_str is None:
            raise Exception('db_connect not set in Config')
        
        con = json.loads(con_str)
        db = MySQLdb.connect(**con)        
        cur = db.cursor()

        return db, cur

    def _row_to_dict(self, 
                     row:Any, 
                     key_map:dict[str, str])->dict[str, Any]:
        db_dct = {}
        for idx, to_key in enumerate(key_map.values()):
            val = get_val(row[idx])
            db_dct[to_key] = val
        
        return db_dct

    def sync_db_done(self):
        db = None
        result = []
        dct = None

        try:
            db, cur = self._load_db_sync_info()
            if db is None:
                return True, None
            
            result = self.pt.query_db(cur)
            for row in result:
                dct = self._row_to_dict(row, self.pt.KEY_MAP)
                self.pt.change_dict(dct)
                self.save_dict(dct)

            self.pt.query_offset += len(result)

        except Exception as e:
            print(f'{dct}:{e}')

        finally:
            if is_some(result):
                result = []

            if is_some(db):
                db.close()
                db = None
        
        return len(result) < self.pt.LIMIT_ONCE

    def proc_db_tbl(self, pt:ProcTable):
        self.pt = pt
        while self.sync_db_done():
            ...

    def save_dict(self, dct:dict[str,Any]):
        if self.pt.DB_TYPE == 'User':
            self.save_user(dct)
        elif self.pt.DB_TYPE == 'Artifact':
            self.save_artifact(dct)
        return None

    def save_user(self, dct:dict[str,Any]):
        pkvs = User.make_pkeys(**dct)
        obj, _ = User.objects.get_or_create(**pkvs)
        changed = self._set_new_attr(obj, dct)

        if changed: 
            obj.save()
            print(f'updated:{obj}')

    def save_artifact(self, dct:dict[str,Any]):
        dct['typ'] = self.pt.ID_TYPE
        pkvs = Artifact.make_pkeys(**dct)
        obj, _ = Artifact.objects.get_or_create(**pkvs)

        dct_rlt = Util.pop_key(dct, 'rlt')
        dct_stg = Util.pop_key(dct, 'stg')
        changed = self._set_new_attr(obj, dct)
        if is_some(dct_stg):
            self._set_stage(obj, dct_stg)
        if is_some(dct_rlt):
            self._set_relate(obj, dct_rlt)
        if changed:
            obj.save()
            print(f'updated:{obj}')

    def _set_new_attr(self, obj:Artifact, dct:dict[str,Any]):
        changed = False
        diff = self.get_diff_attr(obj, dct)
        if len(diff) > 0:
            if self.set_obj_changed(obj, dct, diff):
                changed = True
        return changed


    def _get_rel_arb(self, obj:Any, re:dict[str, Any]):
        ''' if id is 0/''/None, returns None '''
        uid = re['art_a'] if 'art_a' in re else re['art_b']
        if uid is None or uid <= 0:
            return None
        typ = re['typ']
        rlt = re['rlt']

        pkvs = Artifact.make_pkeys(typ = typ, uid = uid)
        obj2, _ = Artifact.objects.get_or_create(**pkvs)
        
        (oa, ob) = (obj2, obj) if 'art_a' in re else (obj, obj2)
        rel, _ = Relation.objects.get_or_create(art_a=oa, rlt=rlt, art_b=ob)
        return rel

    def _set_relate(self, obj:Artifact, obj_rlt:list[dict[str,Any]]):
        obj_rls = {}
        rlts = Relation.objects.filter(art_a=obj).all()
        if len(rlts) > 0:
            for rel in rlts:
                obj_rls[str(rel)] = rel

        for re in obj_rlt:
            rel = self._get_rel_arb(obj, re, True)
            if rel is None: continue

            rel_key = str(rel)
            if rel_key in obj_rls:
                # nothing.
                del obj_rls[rel_key]

        for rel in obj_rls.values():
            rel.delete()
        

    def _set_stage(self, obj:Artifact, stg:dict[str,Any]):
        is_new = False
        if obj.stg is None:
            pkvs= ArtStage.make_pkeys(art=obj)
            nstg, is_new = ArtStage.objects.get_or_create(**pkvs)
            obj.stg = nstg

        diff = None if is_new else self.get_diff_attr(obj.stg, stg)
        if is_new or len(diff) > 0:
            self.set_obj_changed(obj.stg, stg, diff)
            obj.stg.save()
    
    def get_db_mod(self, cls_typ:Any, pkv:dict[str,Any]):
        dc = cls_typ.objects.filter(**pkv)
        if len(dc) == 0:
            return None
        return dc[0]
    
    def get_diff_attr(self, obj1:Any, dct:dict[str,Any])->list[Any]:
        ''' without stg & rlt '''
        diff:list[Any] = []
        for k, v in dct.items():
            if hasattr(obj1, k):
                attr_v = get_val(getattr(obj1, k))
                if attr_v != v:
                    diff.append(k)
        return diff
    
    def set_obj_changed(self, obj:Any, kvs:dict[str, Any], diff:list[str]|None):
        really_changed = False

        dct = kvs.keys() if diff is None else diff
        for k in dct:
            v = kvs[k]
            if isinstance(v, dict) and 'act' in v:
                v = self.get_db_mod(User, v)
            
            old_v = getattr(obj, k)
            if old_v != v:
                setattr(obj, k, v)
                really_changed = True

        return really_changed
    