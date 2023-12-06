from work_hours import WorkHours
from fkb.controls.util_wd import *


def mov_ave(lst, window_size):
    aves = []
    for i in range(len(lst)):
        bef = max(0, i - window_size)
        sub_lst = lst[bef:i+1]
        s = sum(sub_lst)
        a = s / len(sub_lst)
        aves.append(a)
    return aves


def dct_to_lst_sorted(date_value_dct):
    dvs = [(dt, val) for dt, val in date_value_dct.items()]
    dvs.sort(key=lambda x:x[0])
    return dvs


def accumulate_val(date_pts_list_sorted_by_date):
    dpls = date_pts_list_sorted_by_date
    ttl = 0
    for idx, (dt, pts) in enumerate(dpls):
        ttl += pts
        dpls[idx] = (dt, ttl)
    return dpls

def fill_daily_zero(date_pts_list_sorted_by_date):
    wh = WorkHours()
    dpls = date_pts_list_sorted_by_date
    result = []
    for i in range(len(dpls) - 1):
        d1, v1 = dpls[i]
        d2, v2 = dpls[i + 1]
        ds = calc_workdays(d1, d2)-1
        dt1 = to_datetime_end(d1)
        for j in range(ds):
            date = wh.add_workdays(dt1, j).date()
            result.append((date, 0))
    result.append(dpls[-1])
    return result

def fill_daily_previous(date_pts_list_sorted_by_date):
    wh = WorkHours()
    dpls = date_pts_list_sorted_by_date
    result = []
    for i in range(len(dpls) - 1):
        d1, v1 = dpls[i]
        d2, v2 = dpls[i + 1]
        ds = calc_workdays(d1, d2)-1
        dt1 = to_datetime_end(d1)
        for j in range(ds):
            date = wh.add_workdays(dt1, j).date()
            result.append((date, v1))
    result.append(dpls[-1])
    return result

def fill_daily_interpolate(date_pts_list_sorted_by_date):
    wh = WorkHours()
    result = []
    dpls = date_pts_list_sorted_by_date
    for i in range(len(dpls) - 1):
        d1, v1 = dpls[i]
        d2, v2 = dpls[i + 1]
        ds = calc_workdays(d1, d2)-1
        diff = v2 - v1
        step = diff / ds
        dt1 = to_datetime_end(d1)
        for j in range(ds):
            value = v1 + step * j
            date = wh.add_workdays(dt1, j).date()
            result.append((date, value))
    result.append(dpls[-1])
    return result