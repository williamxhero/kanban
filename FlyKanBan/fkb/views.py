from typing import Any

from django.shortcuts import render
from django.http import HttpResponse


def index(request:Any):
    from fkb.controls.util import run_scheduler
    next_time = run_scheduler()
    return HttpResponse(f"next run: {next_time}")

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


def kb(request:Any, typ:str, idstr:str):
    ids = idstr.split(',')
    ids = [int(id) for id in ids]
    from fkb.controls.kb import get_data
    kvargs = {
        'typ':typ,
        'ids':ids,
        }    
    return _render(request, get_data, "fkb/kb.html", **kvargs)
