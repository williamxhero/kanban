from datetime import timedelta
import itertools
from typing import Any
from fkb.tools.util import Util

from fkb.models import *

class ProcTable(object):
    DB_TYPE:str = 'Artifact'
    ID_TYPE:str = 'X'
    KEY_MAP:dict[str,str] = {'id':'uid'}
    HAS_DELETE:bool = True
    TABLE_NAME:str = 'table_from'
    LIMIT_ONCE:int = 500
    ID_START_FROM = 0
    query_offset:int = 0
    query:Any = None

    def _hr2dur(self, val:Any):
        ''' hours to duration(timedelta) '''
        try:
            fval = float(val)
        except:
            return None
        if fval <= 0:
            return None
        return timedelta(hours=float(val))

    def _chg_stt(self, dct:dict[str,Any], kv:dict[str,str]):
        stt = Util.pop_key(dct, '_stt')
        if stt is None:
            return None
        if stt in kv:
            stt_val = kv[stt]
            dct['stt'] = stt_val
            return stt_val
        return None

    def _chg_ttl(self, dct:dict[str,Any]):
        ttl = Util.pop_key(dct, '_ttl')
        if ttl is None:
            return
        ttl = ttl[:32]
        dct['ttl'] = ttl
        return ttl

    def _pop_usr(self, dct:dict[str,Any], *keys:Any):
        first_val = None
        for key in keys:
            _key = f'_{key}'
            act = Util.pop_key(dct, _key)
            if act is None or act == '':
                continue
            if first_val is None:
                first_val = act

        if first_val is None: return None
        return {'act':first_val}
    
    def _chg_usr(self, dct:dict[str,Any], key:str, *keys:Any):
        if len(keys) == 0:
            keys = (key,)
        act_val = self._pop_usr(dct, *keys)
        dct[key] = act_val
        return act_val

    def _chg_key(self, dct:dict[str,Any], key:str, *keys:Any):
        if len(keys) == 0:
            nkeys = (f'_{key}',)
        else:
            nkeys = (f'_{k}' for k in keys)
        key_val = Util.pop_key(dct, *nkeys)
        dct[key] = key_val
        return key_val
    
    def sql_where(self, *conds:Any)->str:
        whr = 'where '
        has_cond = False
        for cond in conds:
            if not cond:
                continue
            has_cond = True
            whr += cond
            whr += ' and '

        if not has_cond: return ''
        whr = whr[:-5]
        return whr

    def db_sql(self):
        col_names = list(self.KEY_MAP.keys())
        db_keys = [f'`{key}`' for key in col_names]
        db_keys_str = ','.join(db_keys)
        id_key = db_keys[0]

        whr_id = f'{id_key}>={self.ID_START_FROM}' if self.ID_START_FROM else None
        whr_del = '`deleted`="0"' if self.HAS_DELETE else None
        where = self.sql_where(whr_del, whr_id)
        limit = f' limit {self.LIMIT_ONCE} offset {self.query_offset}' if self.LIMIT_ONCE else ''
        sql = f'select {db_keys_str} from `{self.TABLE_NAME}` {where} order by {id_key} asc{limit}'
        return sql
    
    def query_db_sql(self, sql:str):
        try:
            self.query.execute(sql)
            result = self.query.fetchall()
            result_len = len(result)
            if result_len == 0:
                return []
            return result
        except Exception as e:
            print(e)
            return []

    def query_db(self)->list[Any]:
        sql = self.db_sql()
        return self.query_db_sql(sql)

    def change_dict(self, dct:dict[str,Any])->None:
        ...

    def relation_incharge(self, obj, rlt)->bool:
        ...

class ProcChild(ProcTable):
    
    def _get_type_ids(self, dct, keys:str, uid_is_list:bool):
        val_str = Util.pop_key(dct, keys)
        if not val_str: return None,None

        _idx = keys.rfind('_')
        if _idx < 0: return None, None

        key = keys[_idx+1:]

        if uid_is_list:
            uids = val_str.split(',')
            if len(uids) <= 0: return None, None
            ids = []
            for uid in uids:
                id = to_int(uid)
                if id <= 0: continue
                ids.append(id)
            return key, ids

        return key, to_int(val_str)


    def _chg_rlt_has(self, dct:dict[str, Any], keys:str):
        ''' keys : xxx_Pl, xxx_Pd, xxx_Typ ... '''
        typ, uid_has = self._get_type_ids(dct, keys, True)
        if not typ: return
        for idx, uid in enumerate(uid_has):
            self._append_rlt(dct, False, typ, uid, idx)
    
    def _get_uid_rdr(self, uids:list[int], rdrs_str:str):
        ''' 将 rdrs_str 按照 uids 的长度进行补齐 (用None) '''
        rdrs = rdrs_str.split(',')
        return itertools.zip_longest(uids, rdrs, fillvalue=None)

    def _chg_rlt_ofs(self, dct:dict[str, Any], keys:str, rdrs:str):
        typ, uid_ofs = self._get_type_ids(dct, keys, True)
        if not typ: return

        id_rd = self._get_uid_rdr(uid_ofs, rdrs)
        for uid, rdr in id_rd:
            self._append_rlt(dct, True, typ, uid, rdr)

    def _chg_rlt_of(self, dct:dict[str, Any], key:str, rdr:Any):
        typ, uid_of = self._get_type_ids(dct, key, False)
        if not typ: return
        self._append_rlt(dct, True, typ, uid_of, rdr)


    def _append_rlt(self, dct:dict[str, Any], is_a:bool, 
                    typ:str,
                    uid:Any,
                    rdr:Any=None,):
        uid_int = to_int(uid)
        if uid_int <= 0: return
        
        if 'rlt' not in dct:
            dct['rlt'] = []

        art = Artifact.make_pkeys(uid=uid_int, typ=typ)
        rlt_dct = {
            'art_a': art if is_a else 'this',
            'rlt': 'CN',
            'art_b': 'this' if is_a else art,
            }
        
        rdr_int = to_int(rdr)
        if is_some(rdr):
            rlt_dct['rdr'] = rdr_int
        dct['rlt'].append(rlt_dct)


    def _null_dct_if_key_art_not_exist(self, dct, key:str):
        ''' return if deleted. '''
        
        if 'uid' not in dct: return
        if key not in dct : return

        _idx = key.rfind('_')
        if _idx < 0:
            del dct['uid']
            return True
        
        typ = key[_idx+1:]
        uid = dct[key]

        if not Artifact.objects.filter(typ=typ, uid=uid).exists():
            del dct['uid']
            return True

        return False
    

    def relation_incharge_A(self, obj:Artifact, rel:Relation) -> bool:
        '''只处理: 
        * 子(本体) -> 不同父
        * 父(本体) -> 相同子
        '''
        if rel.art_b == obj: 
            # 本体子:
            # 不同类 父关系: Pd->Pl->It->S->T
            return rel.art_a.typ != obj.typ
        
        elif rel.art_a == obj:
            # 本体父：
            # 同类子关系: Pd->Pd, Pl->Pl, It->It, S->S
            return obj.typ == rel.art_b.typ
        return False

    def relation_incharge_B(self, obj, rel) -> bool:
        '''只处理 本体子'''
        if rel.art_a == obj: 
            # 本体父:
            return False
        
        return rel.art_b == obj
