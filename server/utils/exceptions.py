from ..env import logger
import json
class InvalidKwargs(BaseException):
    def __init__(self, *args: object) -> None:
        logger.error("Arguements were passed to the config function, only Kwargs")                
        super().__init__(*args)
class EmptyParameters(BaseException):
    def __init__(self, *args: object) -> None:
        logger.error("All arguements were empty!")                
        super().__init__(*args)
class FileWriteException(BaseException):
    def __init__(self, *args: object) -> None:
        logger.error("Exception occured when a file was attemping to be written.")                
        super().__init__(*args)
class FileNamingStandardError(BaseException):
    def __init__(self, *args: object) -> None:
        logger.error("Error reading the file standard...")                
        super().__init__(*args)
class EmptyTimeValue(BaseException):
    def __init__(self, *args: object) -> None:
        logger.error("No time value passed")                
        super().__init__(*args)

class WritingReadOnlyDataPool(BaseException):
    def __init__(self, *args: object) -> None:
        logger.error("Writing to a read only data pool")                
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

class UndefinedEndpoint(BaseException):
    ...


class WebRequestError(BaseException):
    def __init__(self, msg: str) -> None:
        logger.error("{}::Had issues decoding".format(msg))
        super().__init__()

class ResponseIsHTML(BaseException):
    def __init__(self, msg: str) -> None:
        logger.error("{} is HTML".format(msg))
        super().__init__()
        
class IntervalError(BaseException):
    def __init__(self, msg: str) -> None:
        logger.error("Supplied interval is lower than current interval")
        super().__init__()
        
