from .endpoint import Endpoint
class OAUTHClient():
    def __init__(self,endpoint:Endpoint, *args,) -> None:
        self.endpoint = endpoint
    
    # def _fetch():
    
    # go_to_auth() -> redirect