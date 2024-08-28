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
        """
        Arguements:
        sessions: (Request.session() or None) Reuse a session
        endpoint: (str) Endpoint name
        """
        # can pass a session object through "session"=Requests.session
        self.session = kwargs.pop("session") if kwargs.get("session") is not None else requests.session() 
        self.endpoint = kwargs.pop("endpoint")

        self.data = ENDPOINTS.get(self.endpoint)
        
        # definitions not required but helpful
        self.endpoints = self.data.get(kwargs.pop("name")) # token, auth, get, etc...
        
        # All required to be here
        self.method = self.endpoints.get("method")
        self.params = self.endpoints.get("params")
        self.url = self.base_url + self.endpoints.get("url")
        self.headers = self.endpoints.get("headers") # format
        self.cookies = self.endpoints.get("cookies") # format
        self.body = self.endpoints.get("params") # format
        self.response = self.endpoints.get("params") # format
        
       
    @classmethod
    def from_endpoint(cls, endpoint: ...):
        return cls(
            **dict({
                "endpoint":endpoint.name,
                "session":endpoint.session            
            } | endpoint.config)
        )
    def __fmt__(self, req: str) -> str:
        """Format wtih string with internal variables

        Args:
            req (str): String to be formated, use format
            {:attribute} for all attributes
            {:attribute.key.key} for dictionaries, stepable

        Returns:
            str: Formatted
        """
        req = req.split(".")
        for idx, key in enumerate(req):
            req[idx] = key.format(*[self for _ in range(key.count("{:"))])
        
        return ".".join(req)  
    
    def __format__(self, format_spec: str) -> str:
        return str(self.__getattribute__(format_spec)) # checks, then calss __getattr__
    
    def __call__(self, **kwargs) -> WebResponse:
        """Make the request from the provided request session
        
        Arguements:
            response: (dict) changes to response object
            request: (dict) changes to response object

        Returns:
            WebResponse: response in correct format
        """
        return self._request(**kwargs)
    def _request(self, **kwargs) -> WebResponse:
        """Make the request from the provided request session
        
        Arguements:
            response: (dict) changes to response object
            request: (dict) changes to response object

        Returns:
            WebResponse: response in correct format
        """
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
        """Format response dictionary into set of keys (with stepable) for response 

        Returns:
            set: _description_
        """
        return set(getKeys(self.response))
    def __getattr__(self, name: str | list): # Returns dict , list , str, int , bool
        """Pull from $endpoint
        To pull from do self.endpoints[key.key.key]
        |-> self.data[$endpoint][key][key][key]
        Args:
            name (str | list): Get

        Returns:
            _type_: _description_
        """
        return WebResponse.step(self.data, name.split(".") if name is str else name)

def getKeys(item: dict,) -> list[str]:
    """Turn dictionary into stepable list of keys

    Args:
        item (dict): Stepable Dictionary

    Returns:
        list[str]: Stepped Keys
    """
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