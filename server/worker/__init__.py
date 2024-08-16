import toml, requests, json, os
from flask import url_for, Flask, request, Response
from ..env import logger, TOML_FILE_PATH, USERS_FILE_PATH
from ..data import UserManager

ftoml = toml.loads(open(TOML_FILE_PATH).read())

users: UserManager = UserManager.from_dict(
    json.loads(open(USERS_FILE_PATH, "r").read())
) if os.path.exists(USERS_FILE_PATH) else UserManager() # TODO (Load Users from storage here)


class Client:
    def __init__(self, name, state_users = []):
        self.name = name
                
        if ftoml.get(self.name) is None: raise toml.TomlDecodeError("Client not found in toml.")

        self.clientId = ftoml[self.name]["client_id"]
        self.clientSecret = ftoml[self.name]["client_secret"]
        self.sandbox = ftoml[self.name]["sandbox"] # Optional (Default is in auth.toml)
        self.endpoints = {
            "token": ftoml[self.name]["token_url"],
            "auth": ftoml[self.name]["auth_url"],
            "userID": {
                "url": ftoml[self.name]["user_id_url"],
                "key": ftoml[self.name]["user_id_key"]
            }
        }
        self.base_url = ftoml[self.name]["sandbox_url"] if self.sandbox else ftoml[self.name]["production_url"]
        self.redirect_url = "/endpoints/" + self.name
        
        self._state_users = state_users

    @property
    def state_users(self):
        return self._state_users
    def set_url(self, url: str):
        self.base_url = url
    def set_sandbox(self, _new: bool):
        self.sandbox = _new
        self.set_url(ftoml[self.name]["sandbox_url"] if _new else ftoml[self.name]["production_url"])

    
    def _post(self, endpoint: str, addHeaders: dict[str, str] = {}, payload: dict = {}, code: tuple[bool, str] = (False, "")) -> dict:
        url = self.base_url +  endpoint
    
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        if not code[0]:
            return self._handle_response(requests.post(url, data=payload, headers=dict(headers | addHeaders)))
        else:
           
            return self._handle_code_response(requests.post(url, data=payload, headers=headers), code[1])


        
    def _handle_response(self, response: Response) -> dict:
        try:

            if response.status_code == 200:
                print(response)
                return response.json()
            else:
                return {
                    "message": "Session invalid with dexcom, refresh... If not during debugging contact",
                    "recieved_code": response.status_code,
                    "recieved_text": response.text
                }, 500
                
        except Exception as e:
            logger.exception(e())
            return {
                    "message": "Session invalid with dexcom, refresh... If not during debugging contact",
                    "error": str(e())
            }, 500
    def _transform_user(self, state: str, uid: str) -> dict:
        for user in self._state_users:
            if user["state"] == state:
                # Will add the usernID to dict of all users
                
                users._make_user(uid)
                # check if user exsists + creates ut uf ut diwsb;t
                users + (uid, self.name, self.get_user(state)) # uid, provider, data
                return str(users.get(uid))
            return {
                "message": "state: {} not found, you fucking suck".format(state)
            }
                
    def _fetch_token(self, authorization_code: str, state: str,  base_url: str, grant_type: str = "authorization_code"):
        logger.info("Fetching Acess Token with Params: Auth Code: {}, State: {}, Redirect Url: {}".format(authorization_code, state, base_url))

        #url = self.base_url +  self.endpoints["token"]

        payload = {
        "grant_type":grant_type,
        "code": authorization_code,
        "redirect_uri": base_url,
        "client_id": self.clientId,
        "client_secret": self.clientSecret
        }


        return self._post(self.endpoints["token"], payload=payload, code=(True, state))
     

        
    def _handle_code_response(self, data: Response, state: str) -> dict:
        data = self._handle_response(data)
        data["state"] = state
        self._state_users.append(data)
        logger.info("Adding StateUser Handling Response: {}, State: {}".format(data, state))
        

        return data

    def get_user(self, state: str, remove: bool = True) -> dict | Response:
        for user in self._state_users:
            if user["state"] == state:
                if remove: self._state_users.remove(user)
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

    def save(self, loc: str | None = None) -> str:
        logger.info("{} is being saved to {}".format(str(self), self.save_file if loc is None else loc))
        open(self.save_file if loc is None else loc, "w").write(json.dumps(self.to_save()))
        return self.save_file if loc is None else loc