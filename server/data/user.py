from ..env import logger
import json, os
from uuid import uuid4
class UserManager:
    def __init__(self, users: dict = {}, save_file: str = "data/users.json") -> None:
        self._users = users
        self.save_file = save_file

    
    def save(self, loc: str | None = None) -> str:
        logger.info("{} is being saved to {}".format(str(self), self.save_file if loc is None else loc))
        open(self.save_file if loc is None else loc, "w").write(json.dumps(self.to_save()))
        return self.save_file if loc is None else loc
        
    @property
    def users(self) -> dict:
        return self._users
    
  
    def get(self, uid: str, provider: str | None = None, autopopulate: bool = False) -> dict | None:
        if provider is not None:
            if self.get(uid) is not None:
                return self.users[uid].get(provider)
            
            return None
        try:
            return self.users[uid]
        except KeyError:
            logger.warning("Key error when trying to get id: {}\n possible users could be {}".format(
                uid,
                ",".join(self.users.keys())
            ))
            if autopopulate: 
                return self._make_user(uid)
            return None
        
    def create_user(self, **kwargs) -> dict:
        return self._make_user(str(uuid4()), **kwargs)
    
    def _make_user(self, uid: str, **kwargs: dict) -> dict | None:
        if self.get(uid, autopopulate=False) is None:
            self.users[uid] = {}
        
        # Make it autopopulate from the kwarg        
        if len(kwargs.keys()) > 0:
            for key in kwargs.keys():
               self.users[uid][key] = kwargs.get(key) # set the providers
      
        return self.get(uid)
    def _remove_user(self, uid: str) -> dict | None:
        if self._users.get(uid) is None:
            return 
        else:
            return self._users.pop(uid)
    def _remove_provider(self, uid: str, provider: str) -> dict | None:
        if self._users.get(uid) is not None:
            if self._users.get(uid).get(provider) is not None:
                return self._users.get(uid).pop(provider)

    def _make_provider(self, uid, provider: str, data: dict):
        return self._make_user(uid, **{provider: data})

    def add(self, uid: str, provider: str, data: dict) -> dict | None:
        return self._make_user(uid, **{provider: data})
    def remove(self, id: str) -> dict | None:
        return self._remove_user(id)
    
    def __add__(self, data: tuple[str, str, dict]) -> dict | None:
        return self._make_user(data[0], **{data[1]: data[2]})
    def __sub__(self, uid: str | tuple) -> dict | None:
        if type(uid) is str:
            return self._remove_user(uid)
        elif type(uid) is tuple:
            return self._remove_provider(uid[0], uid[1])
    @staticmethod
    def from_dict(data: dict):
        return UserManager(**data)
    def to_dict(self) -> dict:
        return {
            "str": self.__repr__(),
            "users": self.users,
            "amount": len(self.users),
            "save_file": self.save_file,
        }
    def to_save(self) -> dict:
        return {
            "users": self.users,
            "save_file": self.save_file,
        }
    def __repr__(self) -> str:
        return "<UserManager>[User Count: {}]".format(len(self.users))