import os
from logging import info
import toml as toml_mod
def as_var(name, _type: any= str, default: None or any = None) -> any or str: # type: ignore
    t = os.environ.get(name)
    if t is not None:
        if _type is not None:
            return _type(t)
        else:
            return t # Defaults as a string
    else:
        return default if default is not None else ""
    
if not os.path.exists("auth.toml"):
    TO_STDOUT = True
    HOST = as_var("host", str, default="0.0.0.0")
    DEBUG = as_var("debug", bool, default=True)
    PORT = as_var("port", int, default=3321)

else:
    toml = toml_mod.loads(open("auth.toml").read())

    TO_STDOUT = True
    HOST = toml["server"]["host"]
    DEBUG = toml["server"]["debug"]
    PORT = toml["server"]["port"]

