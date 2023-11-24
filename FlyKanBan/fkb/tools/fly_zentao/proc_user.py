from fkb.models import *
from fkb.tools.sync_db.proc_table import ProcTable

class ProcUser(ProcTable):
    
    DB_TYPE = 'User'
    SQL_TABLE_NAME = 'zt_user'

    KEY_MAP = {
        'account':'act',
        'truename':'nam',
        'realname':'nck',
        'gender':'gdr',
        'role':'grp',
    }

    def change_dict(self, dct):
        ...