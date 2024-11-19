from server.utils.exceptions import ResponseIsHTML
from .responses import WebResponse
from .request import WebRequest
from requests import Response
from .fmt import EndpointData

"""
Difference between DataResponse and Webresponse

Similarities:
- Accepts Data with Stepping

Differences:
- Returns Results with 

"""

class DataResponse(WebResponse):
    _type = "Data Response"
    
    def __init__(self, uid: str, time: int, 
                 resp: Response,  
                 _format: set, **kwargs: dict):
        super().__init__(resp,_format=_format, **kwargs) # Make sure "endpoint" is there
        self.uid = uid
        self.time = time
        
        if uid is None:
            raise KeyError("No value provided for uid in kwargs")

    def to_dict(self) -> dict:
        return self.data
    def to_data_response(self, **kwargs: dict) -> EndpointData:
        return EndpointData(**dict(
            kwargs | self.to_dict()
        ))
class DataRequest(WebRequest):
    """"""
    _type = "Web Response"

    def __init__(self, uid: str, time: int, **kwargs: dict) -> None:



        super().__init__(**kwargs)
        
        self.uid = uid
        self.time = time
        
        
        ...
    
    # def _build(self) -> None: pass
    def _request(self, mode:str = None, **kwargs) -> DataResponse:
        """Make the request from the provided request session
        
        Arguements:
            response: (dict) changes to response object
            request: (dict) changes to response object

        Returns:
            WebResponse: response in correct format
        """
        # self.params = kwargs # Messing UP
        self.input = kwargs.get("request", {})
        # TODO Certifications / Proxies Implement Here
        
        
       
        try:

            return DataResponse(
                self.uid,
                self.time,
                self._build(mode=mode, **kwargs),
                self.to_response_format(**kwargs.get("response")),
                **kwargs["response"]
            )
        except ResponseIsHTML:
            raise ValueError("Got HTML instead of a resposne")
