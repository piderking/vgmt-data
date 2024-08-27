from typing import Any
import requests
from .responses import WebResponse
import json
from ..env import CONFIG, logger
ENDPOINTS: dict = json.loads(
    open(CONFIG._replace(CONFIG.ENDPOINTS["path"])).read()
) # Load files from config

class WebRequest(object):
    def __init__(self, **kwargs: dict):
        # can pass a session object through "session"=Requests.session
        self.session = kwargs.pop("session") if kwargs.get("session") is not None else requests.session() 

        self.kwargs = kwargs
        
        # definitions not required but helpful
        self.endpoint = kwargs.pop("endpoint")
        self.endpoints = kwargs.pop("endpoints").get(kwargs.pop("name")) # token, auth, get, etc...
        
        # All required to be here
        self.method = self.endpoints.get("method")
        self.params = self.endpoints.get("params")
        self.url = kwargs.pop("base_url") + self.endpoints.get("url")
        self.headers = self.endpoints.get("headers") # format
        self.cookies = self.endpoints.get("cookies") # format
        self.body = self.endpoints.get("params") # format
        
       
    @classmethod
    def from_endpoint(cls, endpoint: ...):
        return cls(
            **dict({
                "endpoint":endpoint.name,
                "session":endpoint.session            
            } | endpoint.config)
        )
    def __fmt__(self, req: str) -> str:
        req = req.split(".")
        for idx, key in enumerate(req):
            req[idx] = key.format(*[self for _ in key.count("{:")])
        
        return ".".join(req)
    def __format__(self, format_spec: str) -> str:
        return str(self.__getattribute__(format_spec)) # checks, then calss __getattr__
    
    def __call__(self, **kwds: Any) -> WebResponse:
        pass
    def _request(self, **kwargs) -> WebResponse:
        # TODO Certifications / Proxies Implement Here
        return WebResponse(self.session.send(requests.Request(**dict({
            "method": self.method,
            "url": self.url,
            "headers": self.__fmt__(self.headers),
            "data": self.__fmt__(self.body),
            "cookies": self.__fmt__(self.cookies)
        } | kwargs["request"])).prepare()),
        self.to_response_format(),
        **kwargs["response"]
        )

    def to_response_format(self) -> set:
        return set(getKeys(self.response))
    def __getattr__(self, name: str | list): # Returns dict , list , str, int , bool
        return WebResponse.step(self.kwargs, [name] if name is str else name)

def getKeys(item: dict,) -> list[str]:
    items = []
    
    for key in item.keys():
        if key.get("type") == "info":
            items.append(key)
        elif key.get("type") == "timestamp":
            items.append()
        elif key.get("type") == "holder":
            for i in getKeys(item[key]["keys"]):
                items.append("key."+ i)
    return items