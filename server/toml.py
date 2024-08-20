import toml as toml_mod
import colorlog, logging, sys
import os
from .utils.config import Config 

def as_var(name, _type: any= str, default: None or any = None) -> any or str: # type: ignore
    """Pull variables from ENV 

    Args:
        name (str): env variable name
        _type (any, optional): Type to cast into. Defaults to str.
        default (None or any, optional): Value it defaults to. Defaults to None.

    Returns:
        any<type(_type)>
    """
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
TOML_FILE = toml_mod.loads(open(TOML_FILE_PATH, "r").read())

CONFIG = Config(
    **dict({
    
    } | TOML_FILE["paths"] | TOML_FILE ) # Create the CONFIG object with everything e.g. CONFIG.USERS["local"]
)