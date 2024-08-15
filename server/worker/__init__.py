import toml, requests
from flask import url_for, Flask, request, Response
from ..env import logger, TOML_FILE_PATH

ftoml = toml.loads(open(TOML_FILE_PATH).read())

users = {
    
}

class Client:
    def __init__(self, name, users = []):
        self.name = name
                
        if ftoml.get(self.name) is None: raise toml.TomlDecodeError("Client not found in toml.")

        self.clientId = ftoml[self.name]["client_id"]
        self.clientSecret = ftoml[self.name]["client_secret"]
        self.sandbox = ftoml[self.name]["sandbox"] # Optional (Default is in auth.toml)
        self.endpoints = {
            "token": ftoml[self.name]["token_url"],
            "auth": ftoml[self.name]["auth_url"],
        }
        self.base_url = ftoml[self.name]["sandbox_url"] if self.sandbox else ftoml[self.name]["production_url"]
        self.redirect_url = "/endpoints/dexcom"
        
        self._users = users
    
    def set_url(self, url: str):
        self.base_url = url
    def set_sandbox(self, _new: bool):
        self.sandbox = _new
        self.set_url(ftoml[self.name]["sandbox_url"] if _new else ftoml[self.name]["production_url"])

    def _post(self, authorization_code: str, state: str,  base_url: str, grant_type: str = "authorization_code"):
        logger.info("Auth Code: {}, State: {}, Base Url: {}".format(authorization_code, state, base_url))

        url = self.base_url +  self.endpoints["token"]

        payload = {
        "grant_type":grant_type,
        "code": authorization_code,
        "redirect_uri": base_url,
        "client_id": self.clientId,
        "client_secret": self.clientSecret
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, data=payload, headers=headers)

        #try:
        print(response.text)
        if response.status_code == 200:

            return self._handle_response(response.json(), state)
        else:
            return {
                "message": "Session invalid with dexcom, refresh... If not during debugging contact"
            }, 500
        """
        
        except Exception as e:
            logger.error("".format(e))
            return {
                "status":404,
                "message":"Error {}".format(str(type(e)))
            }, 402
        
        """

        
    def _handle_response(self, data: dict, state: str) -> dict:
        data["state"] = state
        self._users.append(data)
        if users.get(state) is None:
            users[state] = {}
        users[state][self.name] = data
        return data

    def get_user(self, state: str, remove: bool = False) -> dict | Response:
        for user in self._users:
            if user["state"] == state:
                if remove: self._users.remove(user)
                return user
            
        logger.debug("No found value for {}".format(state))
        return Response({
           "message": "No Found Entry for State: {}".format(state)
        }, 404)
    
    @staticmethod        
    def from_name(name: str):
        return Client(
            name
        )
class ClientAPI:
    def __init__(self, app, clients: list = []):
        self.app = app
        
        self.clients = clients
    

    def add_client(self, client: Client) -> None:
        self.clients.append(client)

    def remove_client(self, name: str) -> None:
        ftoml.__delattr__(name)
        for item in self.clients:
            if item.name == name:
                self.clients.remove(item)
        
        logger.warn("Couldn't find {}, not in list".format(name))
        return False
    
    @staticmethod
    def from_toml(app: Flask, toml: dict = ftoml): # type: ignore
        clients = []
        for client in toml.keys():

            if client == "oauth" or client == "server" or client == "options":
                continue
            else:
                clients.append(Client.from_name(client))
        
        return ClientAPI(app, clients=clients)