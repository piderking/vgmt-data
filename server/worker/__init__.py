import toml

ftoml = toml.loads(open("auth.toml").read())

class Client:
    def __init__(self, name, sandbox:bool = ftoml["options"] *args,):
        self.name = name
        if ftoml.get(self.name) is None: raise toml.TomlDecodeError("Client not found in toml.")
        self.endpoints = {
            "token": ftoml[self.name]["token_url"],
            "auth": ftoml[self.name]["auth_url"],
            

        }
        self.base_url = ftoml[self.name]["sandbox_url"],
    def _post(self,):
        pass
    
    def _handle_response(self, response):
        pass

    