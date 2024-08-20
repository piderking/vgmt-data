from ..env import logger
from typing import Any


class _VResponse:

    def __call__(self, data: dict, code: int, message: str | None = None) -> type:
        return (dict({
            "message": message,
            "code": code,
        } | data if message else {} | data), code)

class _VSuccessResponse(_VResponse):
    def __call__(self, data: dict, code: int, message: str | None = None) -> type:
        logger.info("SUCESS::{}::{}::{}".format(str(code), str(message), str(data)))
        return super().__call__(data, code, message)
class _VWarningResponse(_VResponse):
    def __call__(self, data: dict, code: int, message: str | None = None) -> type:
        logger.warn("WARNING::{}::{}::{}".format(str(code), str(message), str(data)))

        return super().__call__(data, code, message)
    
class _VErrorResponse(_VResponse):
    def __call__(self, data: dict, code: int, message: str | None = None) -> type:
        logger.error("ERROR::{}::{}::{}".format(str(code), str(message), str(data)))

        return super().__call__(data, code, message)      
        
def VSuccessResponse(data: dict, code: int, message: str | None = None) -> tuple[dict, int]:
    print(type(_VSuccessResponse()(data, code=code, message=message)))
    return _VSuccessResponse()(data, code=code, message=message)

def VWarnResponse(data: dict, code: int, message: str | None = None) -> tuple[dict, int]:
    return _VWarningResponse()(data, code=code, message=message)

def VErrorResponse(data: dict, code: int, message: str | None = None) -> tuple[dict, int]:
    return _VErrorResponse()(data, code=code, message=message)