import re
from server.utils.step import step
from ..worker.user import UserManager
from requests import Response
from ..env import logger, CONFIG
from ..response import _VWarningResponse, VWarnResponse
from ..utils.exceptions import UndefinedRequiredDataFeild, WebRequestError, ResponseIsHTML
from ..utils.tokens import OAUTH_TOKEN
from ..utils.log import info, debug, warn
from urllib.parse import urlparse

class WebResponse(object):
    _type = "Web Response"
    def __init__(self, resp: Response, _format: iter, **kwargs: dict):
        """Create WebResponse

        Args:
            resp (Response): Response object
            _format (any(inter)): example dict or possible keys in a set

        Raises:
            WebRequestError: _description_
            UndefinedRequiredDataFeild: _description_
        """
        
        
        _resp = self._handle_response(resp) 
        
        if type(_resp) is tuple:
            logger.warn("{}::Loaded wrongly from {} >> keep reading for more information. {} ".format(str(self), resp.url, _resp))
            raise WebRequestError("WebResponse had issues...request failed code:{}, Response: {}".format(resp.status_code, resp))
        elif type(_resp) is dict:
            self.data: dict = dict( _resp | kwargs ) # add extra data into 

        self.format: list = list(_format.keys()) if type(_format) is dict else list(_format) # Accept either set / dicts
        
        if self._check_format(): raise UndefinedRequiredDataFeild()
        
        # Sucessful Loading
        info("Loaded from {} Sucessfully ".format(self, __name__), type=self._type,)
    
    def __getattr__(self, name: str) -> any: # str | int | dict | none
        """Python Abstraction self.$name --> self.__getattr__(name)

        Args:
            name (str): Data feild name from the response you're requesting

        Raises:
            KeyError: Unable to find requested name in data feild

        Returns:
            str | int | dict:  feild at key $name
        """
        try:
            d = step(self.__getattribute__("data"), name.split("."))
            if d is None:
                return self.__getattribute__(name)
            return d
        except KeyError as e: 
            raise KeyError(*e.args)
    

        
    def _check_format(self) -> bool:
                # Check for Required Values
        for keys in self.data.keys():
            if step(self.data, keys.split(".")) is None:
                warn("Loaded wrongly >> keep reading for more information ", type=self._type,)
                return False
        return
    def _handle_response(self, resp: Response, status_code: int | list[int]=500) -> dict | tuple[dict, int]:
        """Handle Web Request and either read data or spit errors

        Args:
            response (Response): __mod__::requests (Web Request Library) response 
            status_code (int): acceptable status code to be below, or if it matches one of the acceptable status_codes in the list
        Raises:
            ResponseIsHTML: Indicator exception, points that HTML exsists on webpage
        Returns:
            dict: Contents of the response, transforming from json
        """
        try:

            if any([resp.status_code < status_code] if type(status_code) is not list else list(resp.status_code == code for code in status_code)):
                if bool(re.search(r"r<[^>]+>", resp.text)) or resp.text.count("<!DOCTYPE html>", 0, 15) > 0:
                    file = open("./html/error/{}.html".format(urlparse(resp.url).netloc), "w+")
                    file.write(resp.text)
                    file.close()
                    raise ResponseIsHTML("Request at {}".format(resp.url))
                return resp.json()
            else:
                return VWarnResponse({
                    "message": "Session invalid with {}, refresh... If not during debugging contact, code: {}".format(resp.text, resp.status_code),
                    "recieved_code": resp.status_code,
                    "recieved_text": resp.text
                }, 500)
                
        except Exception as e:
            logger.exception(e)
            return VWarnResponse({
                    "message": "Session invalid with {}, refresh... If not during debugging contact".format(resp.text),
                    "error": str(e)
            }, 500) # Commonly Decode Error, if HTML then ResponseIsHTML is thrown
    def to_dict(self) -> dict:
        """Return object as a dict representation

        Returns:
            dict: dictionary representation of the object
        """
        return dict(self.data)
    def __html__(self) -> dict:
        return self.to_dict()
    @classmethod
    def from_response(cls, *args, **kwargs):
        return cls(*args, **kwargs)
        
class TokenResponse(WebResponse):
    _type = "Token Response"
    """Process __mod__::Response into a OAUTH_TOKEN object
    """
    def __init__(self, 
                 resp: Response, 
                 state: str, 
                 _format: set | dict = {
                "access_token",
                "expires_in",
                "token_type",
                "refresh_token"
            }):
        super().__init__(resp, _format, state=state)

    def to_token(self) -> OAUTH_TOKEN:
        """Create an OAUTH_TOKEN from response

        Returns:
            OAUTH_TOKEN: Token Response
        """
        return OAUTH_TOKEN(**self.data)
class RefreshTokenResponse(TokenResponse):
    _type = "Refresh Token Response"
    def __init__(self, 
                 resp: Response, 
                 token: OAUTH_TOKEN, 
                 _format: set | dict ={
                "access_token",
                "expires_in",
                "token_type",
                "refresh_token"
            }):
        self.token = token
        super().__init__(resp, token.state, _format=_format)
        self.token._refresh(self.to_dict()) # Refreshes the token with the response

    
    def to_token(self) -> OAUTH_TOKEN:
        """Create an OAUTH_TOKEN from response

        Returns:
            OAUTH_TOKEN: Token Response
        """
        return self.token
    