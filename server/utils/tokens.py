from typing import Any
from time import time
from .log import warn, debug
from datetime import datetime
class ExpiredToken(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    pass

prexpiration = 10 * 60# # 30 Minutes
class OAUTH_TOKEN:
    def __init__(self, **data: dict):
        
        self.data = data 
        self.EXPIRED = False
        self.create_time = data.get("create_time") or time()
        self.expires_at = ( self.expires_in  - prexpiration ) + self.create_time  # take of the extra time
        
        
    
    def __getattr__(self, name: str) -> Any:
        d = self.data.get(name.replace(" ", "_").strip().lower())
        if d is None:
            warn("Token Object: {} has no key {}, possible keys...\t{}".format(str(self), name, ",".join(self.data.keys())), name="OAUTH_TOKEN", type=str(self.expires_at))
            raise KeyError("Token Object: {} has no key {}, possible keys...\t{}".format(str(self), name, ",".join(self.data.keys())))

        return d
    
    def isExpired(self) -> bool: # self.expires_in is from loading tokened response
        self.EXPIRED  = 0 > self.expires_at - time()
        print(self.EXPIRED)
        if self.EXPIRED:
            debug("Token Expired... needs to be refreshed. Expired {}".format(self.expires_at-self.create_time), name="OAUTH_TOKEN", type=str(self.expires_at))
            raise ExpiredToken()
        
        return self.EXPIRED
    def _refresh(self, refresh_data: dict):
        debug("Refreshed", name="OAUTH_TOKEN", type=str(self.expires_at))
        for key in refresh_data.keys():
            self.data[key] = refresh_data[key]
        
        self.create_time = time() # _refresh calleded if ExpiredToken
        self.expires_at = self.expires_in  + self.create_time - prexpiration # take of the extra time

        self.isExpired()# <-- todo

        return self
    @classmethod
    def from_dict(cls, **kwargs: dict):
        return cls(**kwargs)
    
    def to_dict(self):
        return dict(self.data | {"isExpired":self.EXPIRED, "create_time":self.create_time, "expires_at": self.expires_at, "time_until_expiration":self.expires_at - time()})
    def __call__(self) -> Any:
        return self.to_dict()
    def __html__(self) -> dict | str:
        return dict(self.data | {"isExpired":self.EXPIRED, "create_time":datetime.fromtimestamp(self.create_time).strftime("%Y-%m-%d %H:%M:%S"), "expires_at": datetime.fromtimestamp(self.expires_at).strftime("%Y-%m-%d %H:%M:%S"), "time_until_expiration":self.expires_at - time()})
