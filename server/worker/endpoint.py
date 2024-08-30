import toml, requests, json, os
from flask import url_for, Flask, request, Response
from ..env import logger, CONFIG
from ..data.responses import UserManager
from ..utils.exceptions import EndpointDefinitionMissing
from ..utils.tokens import OAUTH_TOKEN, ExpiredToken
from ..response import VSuccessResponse, VErrorResponse
from ..data.responses import WebResponse, TokenResponse, RefreshTokenResponse
from ..data.request import WebRequest
users: UserManager = UserManager.load()
ENDPOINTS: dict = json.loads(
    open(CONFIG._replace(CONFIG.ENDPOINTS["path"])).read()
) # Load files from config
class Endpoint:
    def __init__(self, name: str, tokens: list[dict | OAUTH_TOKEN] = []):
        """Endpoint utility class, utilized by EndpointManager
        
        Makes requests and gets access to tokens, however tokens that weren't assigned to a user before the shut off aren't saved for security concerns

        TODO:
            - Track Time of Token
            - Revalidate Token
        
        Args:
            name (str): _description_
            state_users (list or OAUTH_TOKEN, optional): Exisiting OAUTH Tokens for this, should be empty.

        Raises:
            EndpointDefinitionMissing: If the endpoint name is not found in <config_path>/endpoints.json 
        """
        self.name = name
        if ENDPOINTS.get(self.name) is None: raise EndpointDefinitionMissing("Endpoint: {} not found".format(self.name))

        self.session = requests.Session()
        self.config = ENDPOINTS[self.name]
        self.clientId = self.config["client_id"]
        self.clientSecret = self.config["client_secret"]
        self.sandbox = self.config["sandbox"] # Optional (Default is in auth.toml)
        self.endpoints = self.config["endpoints"]
        self.scopes = self.config["scopes"]
        self.base_url = self.config["urls"]["sandbox"] if self.sandbox else self.config["urls"]["production"]
        
        # Redirect URL
        self.redirect_url = CONFIG.OAUTH["redirect_url"] + self.name
        
        # Avaliable Tokens
        # TODO (Make not in memory --> could get huge)
        self._tokens: list[OAUTH_TOKEN] = list(map(lambda token: OAUTH_TOKEN(**token) if type(token) is dict else token, tokens))

    @property
    def tokens(self) -> list[OAUTH_TOKEN]:
        """Unclaimed Authorized Tokens

        Returns:
            list[OAUTH_TOKEN]: List of unclaimed authorization tokens 
        """
        return self._tokens
    
    def set_sandbox(self, _new: bool) -> bool:
        """Sets sandbox and base_url

        Args:
            _new (bool): New Val

        Returns:
            bool: value
        """
        self.sandbox = _new
        self.base_url = (self.config["urls"]["sandbox"] if self.sandbox else self.config["urls"]["production"])
        return _new
    
    def _get(self, endpoint: str, addHeaders: dict[str, str] = {}, payload: dict = {}, code: tuple[bool, str] = (False, "")) -> dict:
        url = self.base_url +  endpoint
    
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        if not code[0]:
            return self._handle_response(requests.post(url, data=payload, headers=dict(headers | addHeaders)))
        else:
            return self._handle_code_response(requests.post(url, data=payload, headers=headers), code[1])

    
    def _post(self, endpoint: str, payload: dict,**kwargs: dict ) -> WebResponse | TokenResponse | RefreshTokenResponse:
        url = self.base_url +  endpoint
    
        headers = dict({"Content-Type": "application/x-www-form-urlencoded"} | kwargs["headers"] if kwargs.get("headers") else {})

        if type(kwargs.get("token")) is OAUTH_TOKEN:
            return RefreshTokenResponse(requests.post(url, data=payload, headers=headers), kwargs["token"])
        elif type(kwargs.get("state")) is str:
            return TokenResponse(requests.post(url, data=payload, headers=headers), kwargs["state"])
        
        return WebResponse(requests.post(url, data=payload, headers=headers), {}) 



    
    
    # Token Section
    def _fetch_token(self, authorization_code: str, state: str,  redirect_url: str, grant_type: str = "authorization_code"):
        logger.info("Fetching Acess Token with Params: Auth Code: {}, State: {}, Redirect Url: {}".format(authorization_code, state, redirect_url))


        payload = {
        "grant_type":grant_type,
        "code": authorization_code,
        "redirect_uri": redirect_url,
        "client_id": self.clientId,
        "client_secret": self.clientSecret
        }

        print(payload)
        n = self._post(self.endpoints["token"],payload, state=state)
        
        self._tokens.append(n.to_token())
        
        return n
    
    
    
    # Token Verification Logic
    def _refresh_token(self, token: OAUTH_TOKEN) -> OAUTH_TOKEN:
        payload = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
        "client_id": self.clientId,
        "client_secret": self.clientSecret
        }


        print(payload)

        return self._post(self.endpoints["refresh"], payload, token=token).to_token()
    
    def _verify_token(self, token:OAUTH_TOKEN) -> OAUTH_TOKEN:
        """Abstraction + Helping Method -> Interact with OAuthToken Object
            

        Args:
            token (OAUTH_TOKEN): OAuth Token

        Returns:
            OAUTH_TOKEN: Verified OAuth Token
        """
        try:
            
            logger.info("Trying to get TOKEN::={}::{}".format(str(token.isExpired()), token.access_token is not None))
        except ExpiredToken:
            logger.warning("Token Expired...Refreshing")
            return self._refresh_token(token)

    
    
    # User Section
    def _transform_user(self, state: str, uid: str) -> dict:
        for token in self.tokens:
            if token.state == state:
                # Will add the usernID to dict of all users
                
                users._make_user(uid) # TODO Make this error for no exsisiting user
                # check if user exsists + creates a entry for this provider
                users._make_provider(uid, self.name, self.get_user(state)) # uid, provider, data
                return users.get(uid)
            return {
                "message": "state: {} not found, you fucking suck".format(state)
            }
    def get_user(self, state: str, remove: bool = True) -> OAUTH_TOKEN | Response:
        for idx, token in enumerate(self.tokens):
            if token.state == state:
                if remove: self._tokens.pop(idx)
                return token
            
        return {
           "message": "{} No Token Found Entry for : {}".format(self.name, state)
        }, 404
    
    
    # Utility Section
    def to_dict(self) -> dict:
        return {
            "name":self.name,
            "client_id":"".join(["#" for _ in self.clientId[:len(self.clientId) - 5]]) + self.clientId[len(self.clientId) - 5:],
            "client_secret": "".join(["#" for _ in self.clientSecret[:len(self.clientSecret) - 5]]) + self.clientSecret[len(self.clientSecret) - 5:],
            "base_url": self.base_url,
            "redirect_url": self.redirect_url,
            "endpoints": self.endpoints,
            "tokens": [token.to_dict() for token in self.tokens],
            "sandbox": self.sandbox,
        }
    @staticmethod        
    def from_name(name: str):
        return Endpoint(
            name
        )

class EndpointManager:
    def __init__(self, *args, **kwargs):
        """Endpoint Manager
        
        Stores the endpoints, accessed through two methods
        ```python
        ep = EndpointManager()
        # 1
        ep.endpoint_name
        
        # 2
        ep.clients["endpoint_name"]
        ```
        > To edit config for the endpoint manager edit the endpoints.json or auth.toml
        > Endpoint's aren't saved between sessions, reauthentication is required
        """
        self.clients = {
            endp_name: Endpoint(endp_name) for endp_name in ENDPOINTS.keys()
        }

    def __getattr__(self, name: str) -> any:
        # self.clients[name]
        try:
            return self.clients[name]
        except KeyError as e:
            logger.error("{} doesn't exsist".format(name))
            print(self.clients.keys())
            raise KeyError("{} doesn't exsist".format(name))
    def add_client(self, client: Endpoint) -> None:
        self.clients[client.name] = client

    def remove_client(self, name: str) -> None:
        """
        Not Implemented
        """
        """ftoml.__delattr__(name)
        for item in self.clients:
            if item.name == name:
                self.clients.remove(item)
        
        logger.warn("Couldn't find {}, not in list".format(name))
        return False
        )"""
        ...
    

def verify_token(token_key: str | None = None):
        """Verify all tokens in a function request

        Args:
            token_key (str, optional): special token only want to be verified in the kwargs
            
        """
        def decorator(function):
            def wrapper(*args, **kwargs):
                self: Endpoint = args[0] # Self
                if token_key is None:
                    for idx, arg in enumerate(args):
                        if type(arg) is OAUTH_TOKEN:
                            args[idx] = self._verify_token(arg)
                        # If not OAUTH Token then pass through
                    for key, val in zip(kwargs.keys(), kwargs.values()):
                        if type(val) is OAUTH_TOKEN:
                            kwargs[key] = self._verify_token(val)
                        # If not OAuth Token then pass through
                else:
                    if type(kwargs.get(token_key)) is OAUTH_TOKEN:
                        kwargs[token_key] = self._verify_token(kwargs.get(token_key))
                    # Else Default
                # Finished Result Sent Back
                result = function(*args, **kwargs)
                return result
            return wrapper
        return decorator