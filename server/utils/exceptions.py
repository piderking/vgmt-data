from ..env import logger
import json
class InvalidKwargs(BaseException):
    def __init__(self, *args: object) -> None:
        logger.error("Arguements were passed to the config function, only Kwargs")                
        super().__init__(*args)

class SavingError(OSError):
    def __init__(self, *args: object) -> None:
        logger.error("Issue Saving the Object see, utils/saving.py")                
        super().__init__(*args)

class LoadingError(BaseException):
    def __init__(self, msg: str) -> None:
        logger.error("{}::Had issues decoding".format(msg))
        super().__init__()


class SerializeError(BaseException):
    def __init__(self, msg: str) -> None:
        logger.error("{}::Had issues deserializing, missing to .to_dict() method".format(msg))
        super().__init__()

        
class EndpointDefinitionMissing(Exception):
    ...
    
class UndefinedRequiredDataFeild(BaseException):
    ...

class WebRequestError(BaseException):
    def __init__(self, msg: str) -> None:
        logger.error("{}::Had issues decoding".format(msg))
        super().__init__()

class ResponseIsHTML(BaseException):
    def __init__(self, msg: str) -> None:
        logger.error("{} is HTML".format(msg))
        super().__init__()