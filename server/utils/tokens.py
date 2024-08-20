from typing import Any


class OAUTH_TOKEN:
    def __init__(self, **data: dict):
        self.data = data 
    def __getattr__(self, name: str) -> Any:
        d = self.data.get(name.replace(" ", "_").strip().lower())
        if d is None:
            raise KeyError("Token Object: {} has no key {}, possible keys...\t{}".format(str(self), name, ",".join(self.data.keys())))
    def _expire(self):
        del self
    def _refresh(self):
        ...
    @classmethod
    def from_dict(cls, **kwargs: dict):
        return cls(**kwargs)
    
    def to_dict(self):
        return self.data
    def __call__(self) -> Any:
        return self.to_dict()
    