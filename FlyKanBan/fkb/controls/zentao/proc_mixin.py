from datetime import date
from typing import Any
from FlyKanBan.fkb.models import is_some
from fkb.controls.util import Util

class ProcPriMixin(object):
    def _chg_pri(self, dct:dict[str,Any]):
        pri = Util.pop_key(dct, '_pri')
        if pri is None:
            return
        if pri == '1':
            dct['pri'] = 'HI'  # 高
        elif pri == '2':
            dct['pri'] = 'MI+' # 中
        elif pri == '3':
            dct['pri'] = 'MI' # 常
        elif pri == '4':
            dct['pri'] = 'LO' # 低
        elif pri == '5':
            dct['pri'] = 'LO-' # 微
    


class ProcSttByDateMixin(object):
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