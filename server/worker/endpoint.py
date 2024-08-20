import toml, requests, json, os
from flask import url_for, Flask, request, Response
from ..env import logger, CONFIG
from ..data import UserManager
from ..utils.exceptions import EndpointDefinitionMissing
from ..utils.tokens import OAUTH_TOKEN
from ..response import VSuccessResponse, VErrorResponse

users: UserManager = UserManager.load()
ENDPOINTS: dict = json.loads(
    open(CONFIG._replace(CONFIG.ENDPOINTS["path"])).read()
)
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
        self._tokens: list[OAUTH_TOKEN] = list(map(lambda token: OAUTH_TOKEN(**token) if type(token) is dict else token, tokens))

    @property
    def tokens(self):
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
    
    
    def _post(self, endpoint: str, addHeaders: dict[str, str] = {}, payload: dict = {}, code: tuple[bool, str] = (False, "")) -> dict:
        url = self.base_url +  endpoint
    
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        if not code[0]:
            return self._handle_response(requests.post(url, data=payload, headers=dict(headers | addHeaders)))
        else:
            return self._handle_code_response(requests.post(url, data=payload, headers=headers), code[1])


        
    def _handle_response(self, response: Response) -> dict:
        """Handle Web Request and either read data or spit errors

        Args:
            response (Response): __mod__::requests (Web Request Library) response 

        Returns:
            dict: Contents of the response, transforming from json
        """
        try:

            if response.status_code < 300:
                return response.json()
            else:
                return {
                    "message": "Session invalid with {}, refresh... If not during debugging contact".format(self.name),
                    "recieved_code": response.status_code,
                    "recieved_text": response.text
                }, 500
                
        except Exception as e:
            logger.exception(e())
            return {
                    "message": "Session invalid with {}, refresh... If not during debugging contact".format(self.name),
                    "error": str(e())
            }, 500
    
    def _handle_code_response(self, data: Response, state: str) -> dict:
        data = self._handle_response(data)
        data["state"] = state
        
        # Transform dict into _token object 
        self.tokens.append(OAUTH_TOKEN(**data))
        logger.info("Adding StateUser Handling Response: {}, State: {}".format(data, state))
        
        return data
       
    def _transform_user(self, state: str, uid: str) -> dict:
        for token in self.tokens:
            if token.state == state:
                # Will add the usernID to dict of all users
                
                users._make_user(uid)
                # check if user exsists + creates a entry for this provider
                users._make_provider(uid, self.name, self.get_user(state)) # uid, provider, data
                return users.get(uid)
            return {
                "message": "state: {} not found, you fucking suck".format(state)
            }
                
    def _fetch_token(self, authorization_code: str, state: str,  base_url: str, grant_type: str = "authorization_code"):
        logger.info("Fetching Acess Token with Params: Auth Code: {}, State: {}, Redirect Url: {}".format(authorization_code, state, base_url))


        payload = {
        "grant_type":grant_type,
        "code": authorization_code,
        "redirect_uri": base_url,
        "client_id": self.clientId,
        "client_secret": self.clientSecret
        }


        return self._post(self.endpoints["token"], payload=payload, code=(True, state))
     

        

    def get_user(self, state: str, remove: bool = True) -> dict | Response:
        for user in self.tokens:
            if user.state == state:
                if remove: self._tokens.remove(user)
                return user
            
        return {
           "message": "{} No Token Found Entry for : {}".format(self.name, state)
        }, 404
    
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
        """
        self.clients = {
            endp_name: Endpoint(endp_name) for endp_name in ENDPOINTS.keys()
        }

    def __getattr__(self, name: str) -> any:
        # self.clients[name]
        try:
            return self.clients[name]
        except KeyError as e:
            raise KeyError(*e.args)
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
    


