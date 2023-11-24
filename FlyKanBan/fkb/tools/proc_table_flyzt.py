from fkb.models import Config
from fkb.tools.sync_db.sync_db import SyncDb
from fkb.tools.calc_data import CalcData



class PTFZT():
    sdb = SyncDb()

    def sync_user(self):
        val = Config.get('sync_user', 'true')
        if val.lower() == 'true':
            from fkb.tools.fly_zentao.proc_user import ProcUser
            self.sdb.proc_db_tbl(ProcUser())
    
    def sync_prod(self):
        from fkb.tools.fly_zentao.proc_prod import ProcProd, ProcEntry
        self.sdb.proc_db_tbl(ProcEntry())
        self.sdb.proc_db_tbl(ProcProd())
    
    def sync_plan(self):
        from fkb.tools.fly_zentao.proc_plan import ProcPlan
        self.sdb.proc_db_tbl(ProcPlan())
    
    def sync_itor(self):
        from fkb.tools.fly_zentao.proc_itor import ProcItor
        self.sdb.proc_db_tbl(ProcItor())
    
    def sync_story(self):
        from fkb.tools.fly_zentao.proc_story import ProcStory
        self.sdb.proc_db_tbl(ProcStory())
    
    def sync_task(self):
        from fkb.tools.fly_zentao.proc_task import ProcTask
        self.sdb.proc_db_tbl(ProcTask())
    
    def sync_bug(self):
        from fkb.tools.fly_zentao.proc_bug import ProcBug
        self.sdb.proc_db_tbl(ProcBug())

    def sync_all(self):
        cd = CalcData()

        #self.sync_user()
        self.sync_prod()
        self.sync_plan()
        
        self.sync_itor()
        cd.calc_itor_tim()

        self.sync_story()
        self.sync_task()
        cd.calc_sty_stgs()
        
        #self.sync_bug()

'''
from fkb.tools.proc_table_flyzt import PTFZT
p = PTFZT()
p.sync_task()

from fkb.tools.proc_table_flyzt import PTFZT
p = PTFZT()
p.sync_story()


from fkb.tools.proc_table_flyzt import PTFZT
p = PTFZT()
p.sync_all()

'''

    