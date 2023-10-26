from datetime import date, timedelta
from typing import Any
from FlyKanBan.fkb.controls.util import Util

from fkb.models import *

class ProcTable(object):
    DB_TYPE:str = 'Artifact'
    ID_TYPE:str = 'X'
    KEYS:list[str] = ['typ', 'uid']
    KEY_MAP:dict[str,str] = {'id':'uid'}
    HAS_DELETE:bool = True
    TABLE_NAME:str = 'table_from'
    LIMIT_ONCE:int = 500
    ID_START_FROM = 0
    query_offset:int = 0

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

    def query_db(self, cur:Any)->list[Any]:
        try:
            cur.execute(self.db_sql())
            result = cur.fetchall()
            result_len = len(result)
            if result_len == 0:
                return []
            return result
        except Exception as e:
            print(e)
            return []

    def change_dict(self, dct:dict[str,Any])->None:
        ...


class ProcChild(ProcTable):
    def _chg_children(self, dct:dict[str, Any], key:str):
        art_has_str = Util.pop_key(dct, key)
        art_has = self._get_pls(art_has_str)
        if art_has:
            dct['rlt'] = art_has

    def _get_pls(self, arts_str:str|None)->list[Any]|None:
        if not arts_str: return
        arts = arts_str.split(',')
        if len(arts) <= 0: return
        rlt:list[Any] = []
        for art in arts:
            art_id = int(art)
            if art_id <= 0: continue
            rlt.append({'typ':self.ID_TYPE, 'art_b':art_id, 'rlt':'CN' })

        return rlt if len(rlt) > 0 else None
    
