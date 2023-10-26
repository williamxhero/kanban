from fkb.models import *
from fkb.controls.zentao.proc_table import ProcTable

class ProcStory(ProcTable):
    KEY_MAP = {
        'id':'uid',
        'title':'ttl',
        'estPts':'pnt_est',
        'version':'ver',

        'pri':'_pri',
        'status':'_stt',
        'openedDate':'_crt_tim',
        'openedBy':'_crt_usr',
        'closedDate':'_cls_tim',
        'closedBy':'_cls_usr',

        'completeStage':'_stages',

        # rel:
        'product':'_prod_to',
        'plan':'_plan_to',

        'childStories':'_stories_has',
        'linkStories':'_stories_lnk',

        'reviewedDate':'_rev_end_tim',
        'revewedBy':'_rev_usr',
        'examinedDate':'_acc_end_tim',
        'examinedBy':'_acc_usr',

        
    }

    TABLE_NAME = 'zt_story'
    ID_START_FROM = 6879

    def __init__(self) -> None:
        super().__init__()

    def _run_sql(self, sql):
        # select all zt_task.story from zt_story 
        # where zt_task.id > 6879
        ...
    
    def change_dict(self, dct):
        dct['typ'] = 'R'