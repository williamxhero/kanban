from typing import Any
from datetime import datetime, timedelta

from work_hours import WorkHours

class Util:

    @staticmethod
    def get_key(dct:dict[str, Any], *keys:Any)->Any:
        ''' pop the key from dict, return the first 
        not-None value.
        '''
        val = None
        for key in keys:
            if key in dct:
                v = dct[key]
                if val is None:
                    val = v
        return val

    @staticmethod
    def pop_key(dct:dict[str, Any], *keys:Any)->Any:
        ''' pop the key from dict, return the first 
        not-None value.
        '''
        val = None
        for key in keys:
            if key in dct:
                v = dct[key]
                del dct[key]
                if val is None:
                    val = v
        return val
    

    wh = WorkHours()

    @classmethod
    def calc_work_dur(cls, start_dt:datetime, end_dt:datetime, psd_hr:float=0):
        ''' 计算两个日期之间 的工时 减去 暂停时长 '''
        if not start_dt or not end_dt:
            return None
        dv_dur = cls.wh.calc(start_dt, end_dt)
        dv_dur -= psd_hr
        if dv_dur <= 0:
            dv_dur = 0
        return timedelta(hours=dv_dur)
    


class Print:
    lst_dot = False

    @classmethod
    def log(cls, str):
        if cls.lst_dot:
            print()
            cls.lst_dot = False
        print(str)
        return True

    @classmethod
    def dot(cls):
        print('.', end='')
        cls.lst_dot = True
        return False
