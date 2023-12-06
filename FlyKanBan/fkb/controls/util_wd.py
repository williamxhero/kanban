from datetime import timedelta, datetime, date

from work_hours import WorkHours


def to_datetime_start(dt:date):
    if isinstance(dt, datetime): return dt
    if isinstance(dt, date):
        return datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    return dt

def to_datetime_end(dt:date):
    if isinstance(dt, datetime): return dt
    if isinstance(dt, date):
        return datetime(dt.year, dt.month, dt.day, 23, 59, 59)
    return dt


def calc_workdays(start:date, end:date):
    ''' from start to end, how many workdays are there.
    including both start and end.
    '''
    if start > end: start, end = end, start
    stt_dt = to_datetime_start(start)
    end_dt = to_datetime_end(end)
    cnt = 0
    wh = WorkHours()
    while stt_dt < end_dt:
        if wh.is_workday(stt_dt):
            cnt+=1
        stt_dt += timedelta(days=1)
    return cnt
