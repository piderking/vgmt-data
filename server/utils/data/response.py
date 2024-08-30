from ...data.responses import WebResponse
from ...data.request import WebRequest
from requests import Response
from .data import EndpointData

"""
Difference between DataResponse and Webresponse

Similarities:
- Accepts Data with Stepping

Differences:
- Returns Results with 

"""

class DataResponse(WebResponse):
    def __init__(self, 
                 resp: Response,  
                 _format: set, **kwargs: dict):
        super().__init__(resp,_format=_format, **kwargs) # Make sure "endpoint" is there
    
    def to_dict(self) -> dict:
        return self.data
    def to_data_response(self, **kwargs: dict) -> EndpointData:
        return EndpointData(**dict(
            kwargs | self.to_dict()
        ))
class DataRequest(WebRequest):
    def __init__(self, **kwargs: dict) -> None:
        super().__init__(**kwargs)
        ...
    
    def _request(self, **kwargs) -> WebResponse:
        return super()._request(**dict(
            kwargs | {
                "request":{
                    
                }, 
                "response":{
                    
                }
            }
    ))