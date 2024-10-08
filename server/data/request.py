from typing import Any
import requests

from server.utils.state import isProduction
from server.utils.step import step
from .responses import WebResponse
from ..utils.exceptions import ResponseIsHTML, UndefinedEndpoint
from ..env import CONFIG, logger
import re
from ..utils.log import debug, info
import json
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
        self.access_token = kwargs.pop("access_token")
        self.data: dict = ENDPOINTS.get(self.endpoint)
        if self.data is None: 
            logger.warn("Endpoint not defined, {}".format(self.endpoint))
            raise UndefinedEndpoint(self.endpoint)
        
        # definitions not required but helpful
        self.endpoints = self.data.get("endpoints") # token, auth, get, etc...
        
        self.path = self.endpoints.get(kwargs["path"])
        
        # All required to be here
        self.method = self.path.get("method")
        self.params = self.path.get("params")
        self.url =  self.path.get("url")
        self.headers = self.path.get("headers") # format
        self.cookies = self.path.get("cookies") # format
        self.body = self.path.get("body") 
        self.response = self.path.get("response") # format    
        self.request = self.path.get("request") # format    

       
    @classmethod
    def from_endpoint(cls, endpoint: ..., **kwargs):
        """
        Endpoint: endpoint to generate from
        
        kwargs:
        sessions: if want to generate sessions
        endpoint: endpoint name to pull data from
        """
        return cls(
            **dict({
                "endpoint":endpoint.name,
                "session":endpoint.session            
            } | kwargs)
        )
    def __fmt__(self, req: str | dict) -> str:
        """Format wtih string with internal variables

        Args:
            req (str): String to be formated, use format
            {:attribute} for all attributes
            {:attribute.key.key} for dictionaries, stepable

        Returns:
            str: Formatted
        """
        
        if type(req) is dict:
            for key, value in req.items():
                req[key] = self.__fmt__(value)
            return req
        req = str(req)
        srch = re.findall(r"\{\:([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}", req)
        
        v = str(req)
        
        if srch is not None:
            
            for idx, key in enumerate(srch):
                
                v = v.replace(str("{:"+key+"}"), str(getattr(self, key)))
                #print("Modify: ({}) -> ({})".format(key, getattr(self, key)))
            info("Formatted: {} -> {}".format(req, v), type="Request", name="Formatter")
            return v
        else:
            return req

    
    def __call__(self, **kwargs) -> WebResponse:
        """Make the request from the provided request session
        
        Arguements:
            response: (dict) changes to response object
            request: (dict) changes to response object

        Returns:
            WebResponse: response in correct format
        """
        return self._request(**kwargs)
    def _request(self, mode:str = None, **kwargs) -> WebResponse:
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
        
        
        data =  self.__fmt__(self.body)
        prep = dict({
            "method": self.method,
            "url": self.urls[mode or isProduction(asStr=True)] + self.url,
            "headers": self.__fmt__(self.headers), # TODO Transformer into a step formatter
            "params":self.__fmt__(self.params), # TODO Format
            "cookies": self.__fmt__(self.cookies)
        } | dict({"data": data} if len(data) > 0 else {}))
        
        info("Prepared Data",prep, type="Request", name="Requester")
        preped = self.session.send(requests.Request(**prep).prepare())
        try:
            return WebResponse(preped,
            self.to_response_format(),
            **kwargs["response"]
            )
        except ResponseIsHTML:
            raise ValueError("Got HTML instead of a resposne")

    def to_response_format(self) -> set:
        """Format response dictionary into set of keys (with stepable) for response 

        Returns:
            set: _description_
        """
        return getKeys(self.response)
    def __getattr__(self, name: str | list): # Returns dict , list , str, int , bool
        """Pull from $endpoint
        To pull from do self.endpoints[key.key.key]
        |-> self.data[$endpoint][key][key][key]
        Args:
            name (str | list): Get

        Returns:
            _type_: _description_
        """
        d = step(self.data, name)
        if d is None:
            splt = str(name).split(".")
            if len(splt) > 1:
                return step(self.__getattribute__(splt[0]), ".".join(splt[:]))
            return self.__getattribute__(name) 
        return d
def getKeys(item: dict,) -> list[str]:
    """Turn dictionary into stepable list of keys

    Args:
        item (dict): Stepable Dictionary

    Returns:
        list[str]: Stepped Keys
    """
    items = []
    
    for key in item.keys():
        if item[key].get("type") == "info":
            items.append(key)
        elif item[key].get("type") == "timestamp":
            items.append(key)
        elif item[key].get("type") == "holder":
            for i in getKeys(item[key]["keys"]):
                items.append("key."+ i)
    return items