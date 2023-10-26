from typing import Any

from django.shortcuts import render
from django.http import HttpResponse
from apscheduler.schedulers.background import BackgroundScheduler
#from django_apscheduler.jobstores import DjangoJobStore

from fkb.controls.sync_db import SyncDb

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

def kanban(request:Any, input:str):
    from fkb.controls.kanban import get_data
    return render(request, "fkb/kanban.html", {'datas':get_data(input)})



