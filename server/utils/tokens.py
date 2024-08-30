from typing import Any
from time import time

class ExpiredToken(Exception):
    pass

prexpiration = 30 * 60 # 30 Minutes
class OAUTH_TOKEN:
    def __init__(self, **data: dict):
        self.data = data 
        self.EXPIRED = False
        self.create_time = data.get("create_time") or time()
        self.expires_at = self.expires_in * 60 + time() - prexpiration # take of the extra time
    
    def __getattr__(self, name: str) -> Any:
        print("Trying to get: {}".format(name))
        d = self.data.get(name.replace(" ", "_").strip().lower())
        if d is None:
            raise KeyError("Token Object: {} has no key {}, possible keys...\t{}".format(str(self), name, ",".join(self.data.keys())))

        return d
    
    def isExpired(self) -> bool: # self.expires_in is from loading tokened response
        self.EXPIRED  = time() - self.create_time > self.expires_in * 60
        
        if self.EXPIRED:
            raise ExpiredToken()
        
        return self.EXPIRED
    def _refresh(self, refresh_data: dict):
        self.create_time = time()
        for key in refresh_data.keys():
            self.data[key] = refresh_data[key]
        self.isExpired()# <-- todo
        self.expires_at = self.expires_in * 60 + time() - prexpiration # take of the extra time

        return self
    @classmethod
    def from_dict(cls, **kwargs: dict):
        return cls(**kwargs)
    
    def to_dict(self):
        return dict(self.data | {"isExpired":self.EXPIRED, "create_time":self.create_time, "time_until_expiration":self.expires_in * 60 - (time() - self.create_time)})
    def __call__(self) -> Any:
        return self.to_dict()
    def __html__(self) -> dict | str:
        return self.to_dict()