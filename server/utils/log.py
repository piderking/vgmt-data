from ..env import logger

def argformat(*args, **kwargs) -> str:
    return "[{}]::({})-{}".format(kwargs.pop("type", "_"), kwargs.pop("name", "_"), ",".join(args),)
    
def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)
def info(*args, **kwargs):
    logger.info(argformat(*args, **kwargs))

def warn(*args, **kwargs):
    logger._warn(argformat(*args, **kwargs))

def error(*args, **kwargs):
    logger._error(argformat(*args,**kwargs))
    