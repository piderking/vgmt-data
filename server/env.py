import os
from logging import info
import toml as toml_mod
import colorlog, logging, sys
def as_var(name, _type: any= str, default: None or any = None) -> any or str: # type: ignore
    t = os.environ.get(name)
    if t is not None:
        if _type is not None:
            return _type(t)
        else:
            return t # Defaults as a string
    else:
        return default if default is not None else ""


# constants 
TOML_FILE_PATH = as_var("TOML_FILE_PATH", str, "auth.toml")
handler = colorlog.StreamHandler()

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)


handler.setFormatter(colorlog.ColoredFormatter(
	'%(log_color)s%(levelname)s:%(name)s:%(message)s'))
if not os.path.exists("auth.toml"):
   raise FileNotFoundError("No auth.toml")

else:
    toml = toml_mod.loads(open("auth.toml").read())

    TO_STDOUT = True
    HOST = toml["server"]["host"]
    DEBUG = toml["server"]["debug"]
    PORT = toml["server"]["port"]

if not TO_STDOUT: logging.basicConfig(filename='logs/server.log', level=logging.INFO)
else: logging.basicConfig(stream=sys.stdout, level=logging.INFO)


