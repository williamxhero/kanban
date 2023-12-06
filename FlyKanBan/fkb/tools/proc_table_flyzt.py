from fkb.models import Config
from fkb.tools.sync_db.sync_db import SyncDb
from fkb.tools.calc_data import CalcData



class PTFZT():
    sdb = SyncDb()
    cd = CalcData()

    def sync_user(self):
        val = Config.get('sync_user', 'true')
        if val.lower() == 'true':
            from fkb.tools.fly_zentao.proc_user import ProcUser
            self.sdb.proc_db_tbl(ProcUser())
    
    def sync_0_prod(self):
        from fkb.tools.fly_zentao.proc_prod import ProcProd, ProcEntry
        self.sdb.proc_db_tbl(ProcEntry())
        self.sdb.proc_db_tbl(ProcProd())
    
    def sync_1_plan(self):
        from fkb.tools.fly_zentao.proc_plan import ProcPlan
        self.sdb.proc_db_tbl(ProcPlan())
    
    def sync_2_itor(self):
        from fkb.tools.fly_zentao.proc_itor import ProcItor
        self.sdb.proc_db_tbl(ProcItor())
        self.cd.calc_itor_tim()

    def sync_3_story(self):
        from fkb.tools.fly_zentao.proc_story import ProcStory
        self.sdb.proc_db_tbl(ProcStory())
    
    def sync_4_task(self):
        from fkb.tools.fly_zentao.proc_task import ProcTask
        self.sdb.proc_db_tbl(ProcTask())
        self.cd.calc_sty_stgs()

    def sync_5_bug(self):
        from fkb.tools.fly_zentao.proc_bug import ProcBug
        self.sdb.proc_db_tbl(ProcBug())

    def sync_all(self):
        #self.sync_user()
        self.sync_0_prod()
        self.sync_1_plan()
        self.sync_2_itor()
        self.sync_3_story()
        self.sync_4_task()
        
        #self.sync_bug()

    