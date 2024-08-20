from typing import Any
from time import time

class OAUTH_TOKEN:
    def __init__(self, **data: dict):
        self.data = data 
        self.EXPIRED = False
        self.create_time = time()
    def __getattr__(self, name: str) -> Any:
        print("Trying to get: {}".format(name))
        d = self.data.get(name.replace(" ", "_").strip().lower())
        
        if d is None:
            raise KeyError("Token Object: {} has no key {}, possible keys...\t{}".format(str(self), name, ",".join(self.data.keys())))
        return d
    def _expire(self) -> bool: # self.expires_in is from loading tokened response
        self.EXPIRED  = time() - self.create_time > self.expires_in * 60
        return self.EXPIRED
    def _refresh(self):
        ...
    @classmethod
    def from_dict(cls, **kwargs: dict):
        return cls(**kwargs)
    
    def to_dict(self):
        return dict(self.data | {"isExpired":self.EXPIRED, "create_time":self.create_time, "time_until_expiration":self.expires_in * 60 - (time() - self.create_time)})
    def __call__(self) -> Any:
        return self.to_dict()
    def __html__(self) -> dict | str:
        return self.to_dict()