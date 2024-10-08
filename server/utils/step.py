from ..utils.log import info, debug, warn


def step(val: dict, keys:list[str] | str): # i love recursive
        keys = keys.split(".") if type(keys) is str else keys
        if len(keys) == 1:

            debug("Stepped through dictionary...Final Results", type="Stepper")
            return val.get(keys[0]) 
        
        elif type(val) is dict:
            key = keys.pop(0)
            if val.get(key) is None:
                return None

            return step(val[key], keys) 
        return val # defaulkts