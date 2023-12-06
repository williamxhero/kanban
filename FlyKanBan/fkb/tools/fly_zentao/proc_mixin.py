from datetime import date
from typing import Any
from fkb.mod_type import to_int
from fkb.models import is_some
from fkb.tools.util import Util

class ProcMixin(object):
    def _chg_pnt(self, dct, key='_pnt'):
        pnt = Util.pop_key(dct, key)
        
        if is_some(pnt):
            int_pnt = float(pnt)
            if 0 < int_pnt < 0.00000001: # n/a
                int_pnt = -1
            dct[key[1:]] = int_pnt

        if key == '_pnt':
            self._chg_pnt(dct, key='_pnt_est')

    def _chg_pri(self, dct:dict[str,Any]):
        pri = Util.pop_key(dct, '_pri')
        pri = to_int(pri)
        if not pri:return

        if pri == 1:
            dct['pri'] = 'HI'  # 高
        elif pri == 2:
            dct['pri'] = 'MIT' # 中
        elif pri == 3:
            dct['pri'] = 'MI' # 常
        elif pri == 4:
            dct['pri'] = 'LO' # 低
        elif pri == 5:
            dct['pri'] = 'LO_' # 微
    
    def _chg_ttl_sht(self, dct:dict[str, Any]):
        ttl = Util.pop_key(dct, '_ttl')
        sht = Util.pop_key(dct, '_sht')
        ttl32 = ttl[:32]
        sht32 = sht[:32]
        dct['ttl'] = ttl32

        if sht32 != ttl32:
            # 不同才保留short
            dct['sht'] = sht[:32]
        else:
            # 相同就不要short了。
            # dct['sht'] = None
            pass

    def _chg_stt_by_date(self, dct:dict[str, Any], key_begin:str, key_end:str):
        begin = dct[key_begin]
        end = dct[key_end]
        today = date.today() 

        if is_some(end) and end < today:
            dct['stt'] = '-GB' # 已结束
            return

        if begin is None:
            dct['stt'] = '-PS' # 待安排
            return

        if begin > today:
            dct['stt'] = '-AP' # 待开始
            return

        dct['stt'] = 'KF-' # 进行中