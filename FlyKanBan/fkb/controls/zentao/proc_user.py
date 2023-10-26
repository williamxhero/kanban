from fkb.models import *
from fkb.controls.proc_table import ProcTable

class ProcUser(ProcTable):
    
    KEYS = ['act']
    DB_TYPE = 'User'
    TABLE_NAME = 'zt_user'

    KEY_MAP = {
        'account':'act',
        'truename':'nme',
        'realname':'nck',
        'gender':'gdr',
        'role':'grp',
    }

    def change_dict(self, dct):
        ...