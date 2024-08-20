from ..env import logger
import json
class InvalidKwargs(Exception):
    def __init__(self, *args: object) -> None:
        logger.error("Arguements were passed to the config function, only Kwargs")                
        super().__init__(*args)

class SavingError(OSError):
    def __init__(self, *args: object) -> None:
        logger.error("Issue Saving the Object see, utils/saving.py")                
        super().__init__(*args)

class LoadingError(json.JSONDecodeError):
    def __init__(self, msg: str, doc: str, pos: int) -> None:
        logger.error("{}::Had issues decoding at position {}".format(doc, pos))
        super().__init__(msg, doc, pos)


        
class EndpointDefinitionMissing(Exception):
    ...