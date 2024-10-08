from ..env import CONFIG

def isProduction(asStr: bool=False) -> bool | str:
    if asStr:
        return "production" if isProduction(False) else "sandbox"
    return bool(CONFIG.OPTIONS["production"])
    

