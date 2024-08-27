from ...data.responses import WebResponse
from ...data.request import WebRequest
from requests import Response

class DataTokenResponse(WebResponse):
    def __init__(self, 
                 resp: dict, # 
                 _format: set | dict ={
                "access_token",
                "expires_in",
                "token_type",
                "refresh_token"
            }):
        super().__init__(resp,_format=_format)

class DataRequest(WebRequest):
    def __init__(self, **kwargs: dict) -> None:
        self.endpoint = kwargs.pop("endpoint")
        self.endpoints = kwargs.pop("endpoints").get(kwargs.pop("name")) # token, auth, get, etc...
        self.method = self.endpoints.get("method")
        
        self.params = self.endpoints.get("params")
        self.url = kwargs.pop("base_url") + self.endpoint.get("url")
        self.headers = self.endpoints.get("headers") # format
        self.body = self.endpoints.get("params") # format
    