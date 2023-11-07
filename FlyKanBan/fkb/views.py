from typing import Any

from django.shortcuts import render
from django.http import HttpResponse
from apscheduler.schedulers.background import BackgroundScheduler

from fkb.tools.sync_db import SyncDb

scheduler = BackgroundScheduler()

def run():
    SyncDb().sync()

def index(request:Any):
    jobs = scheduler.get_jobs()
    if len(jobs) == 0:
        job = scheduler.add_job(run, 'cron', hour='9-19', minute='0')
    else:
        job = jobs[0]
    scheduler.start()
    return HttpResponse(f"last run: {job.next_run_time}")


def _render(request:Any, func, html, **kvargs:Any):
    datas = func(**kvargs)
    if datas is None:
        return HttpResponse("No data")

    return render(request, html, datas)

def pds(request:Any, str_args:str):
    from fkb.controls.pds import get_data
    args = str_args.split('+')
    ongoing = 'ongoing' if 'ongoing' in args else 'all'
    kvargs = {
        'ongoing':ongoing,
        }
    return _render(request, get_data, 'fkb/pds.html', **kvargs)


def pls(request:Any, pd_id:int, str_args:str):
    from fkb.controls.pls import get_data
    args = str_args.split('+')
    ongoing = 'ongoing' if 'ongoing' in args else 'all'
    kvargs = {
        'pd_id':pd_id,
        'ongoing':ongoing,
        }
    return _render(request, get_data, "fkb/pls.html", **kvargs)

def its(request:Any, pl_id:int, str_args:str):
    from fkb.controls.its import get_data
    args = str_args.split('+')
    ongoing = 'ongoing' if 'ongoing' in args else 'all'
    kvargs = {
        'pl_id':pl_id,
        'ongoing':ongoing,
        }
    return _render(request, get_data, "fkb/its.html", **kvargs)


def it(request:Any, it_id:int):
    from fkb.controls.it import get_data
    kvargs = {
        'it_id':it_id,
        }
    return render(request, "fkb/it.html", 
                  get_data(**kvargs) )
