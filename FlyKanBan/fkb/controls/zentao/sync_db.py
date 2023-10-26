


from fkb.models import Config
from fkb.controls.zentao.proc_user import ProcUser

from fkb.controls.zentao.proc_plan import ProcPlan
from fkb.controls.zentao.proc_prod import ProcProd
from fkb.controls.zentao.proc_itor import ProcItor

from fkb.controls.zentao.proc_task import ProcTask
from fkb.controls.zentao.proc_bug import ProcBug
from fkb.controls.zentao.proc_story import ProcStory

from fkb.controls.sync_db import SyncDb


def ProcTable():
    sdb = SyncDb()

    val = Config.get('sync_user', 'true')
    if val.lower() == 'true':
        sdb.proc_db_tbl(ProcUser())

    # sdb.proc_db_tbl(ProcProd())
    # sdb.proc_db_tbl(ProcPlan())
    sdb.proc_db_tbl(ProcItor())

    #sdb.proc_db_tbl(ProcBug())
    #sdb.proc_db_tbl(ProcTask())
    # sdb.proc_db_tbl(ProcStory())


    # from fkb.controls.zentao.sync_db import ProcTable as f
    # f()