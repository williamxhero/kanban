from typing import Any

class Util:

    @staticmethod
    def pop_key(dct:dict[str, Any], *keys:Any)->Any:
        ''' pop the key from dict, return the first 
        not-None value.
        '''
        val = None
        for key in keys:
            if key in dct:
                v = dct[key]
                del dct[key]
                if val is None:
                    val = v
        return val