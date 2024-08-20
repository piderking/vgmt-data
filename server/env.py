import os
from logging import info
import toml as toml_mod
import colorlog, logging, sys

from .toml import CONFIG



logger = colorlog.getLogger(__name__)
handler = colorlog.StreamHandler()
logger.addHandler(handler)


handler.setFormatter(colorlog.ColoredFormatter(
	'%(log_color)s%(levelname)s:%(name)s:%(message)s'))
if not os.path.exists("auth.toml"):
   raise FileNotFoundError("No auth.toml")

else:
    TO_STDOUT = bool(CONFIG.options["to_std_out"])
    HOST = CONFIG.server["host"]
    DEBUG = CONFIG.server["debug"]
    PORT = CONFIG.server["port"]


if not TO_STDOUT: logging.basicConfig(filename='logs/server.log', level=logging.INFO)
else: logging.basicConfig(stream=sys.stdout, level=logging.INFO)



