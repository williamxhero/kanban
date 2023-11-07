


from fkb.models import Config
from fkb.tools.zentao.proc_user import ProcUser

from fkb.tools.zentao.proc_plan import ProcPlan
from fkb.tools.zentao.proc_prod import ProcProd
from fkb.tools.zentao.proc_itor import ProcItor

from fkb.tools.zentao.proc_task import ProcTask
from fkb.tools.zentao.proc_bug import ProcBug
from fkb.tools.zentao.proc_story import ProcStory

from fkb.tools.sync_db import SyncDb


def ProcTable():
    sdb = SyncDb()

    val = Config.get('sync_user', 'true')
    if val.lower() == 'true':
        sdb.proc_db_tbl(ProcUser())

    sdb.proc_db_tbl(ProcProd())
    sdb.proc_db_tbl(ProcPlan())
    sdb.proc_db_tbl(ProcItor())

    sdb.proc_db_tbl(ProcStory())
    sdb.proc_db_tbl(ProcTask())
    sdb.proc_db_tbl(ProcBug())


    # from fkb.tools.sync_db_zt import ProcTable as f
    # f()
