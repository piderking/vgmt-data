from ..env import logger, CONFIG
import json, os
from uuid import uuid4
from ..utils.saving import Saveable
from ..utils.exceptions import LoadingError
import json

class UserManager(Saveable):
    def __init__(self, users: dict = {}) -> None:
        """User Manager, both for Storage Buckets and for Local Saving

        Args:
            users (dict, optional): _description_. Defaults to {}.
        """
        # All Users // LOCAL ONLY
        self._users = users 
        
        # Is Web
        self._local = bool(CONFIG.USERS["local"])
        
        # Do if local
        if self._local:
            ...
        else: # Storage Bucket ._.
            self.web_config = json.loads(open(CONFIG.USERS["web_config"], "r").read())
            ...
        
        super().__init__(file_name=CONFIG.USERS["file_path"])

    def isLocal(self) -> bool:
        return self._local
    
    def save(self) -> str:
        if self.isLocal():
            return super().save()
        else:
            ... # IMplement Storage Bucket
    @classmethod
    def load(cls, file_name: str | None = None): 
        if cls.isLocal():
            try:
                loaded: dict = json.loads(
                        open(CONFIG._valid_directory(file_name), "r").read()
                    )
                return cls(
                    **dict(loaded | {
                        "file_name": file_name
                        }), # Can be changed in subclassing
                )
            except json.JSONDecodeError as e:
                raise LoadingError(e.msg, e.doc, e.pos)
        else:
            ... # Seperate Loading method -- not local
    @property
    def users(self) -> dict:
        if self.isLocal():
            return self._users
        else:
            ...
    
  
    def get(self, uid: str, provider: str | None = None, autopopulate: bool = False) -> dict | None:
        if self.isLocal():
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
        else:...
    def create_user(self, **kwargs) -> dict:
        """Utility Function -- Abstraction
                Creates a user with correct syntax
                Also auto-generates a user
        
        
           
        Returns:
            dict: user info
        """
        return self._make_user(str(uuid4()), **kwargs)
    
    def _make_user(self, uid: str, **kwargs: dict) -> dict | None:
        if self.isLocal():
            if self.get(uid, autopopulate=False) is None:
                self.users[uid] = {}
            
            # Make it autopopulate from the kwarg        
            if len(kwargs.keys()) > 0:
                for key in kwargs.keys():
                    #self.users[uid][key] = kwargs.get(key) # set the providers
                    self._make_provider(uid, key, kwargs[key])
        
            return self.get(uid)
        else:
            ...
    def _remove_user(self, uid: str) -> dict | None:
        if self.isLocal():
            if self._users.get(uid) is None:
                return 
            else:
                return self._users.pop(uid)
        else:
            ...
    def _remove_provider(self, uid: str, provider: str) -> dict | None:
        if self.isLocal():
            if self._users.get(uid) is not None:
                if self._users.get(uid).get(provider) is not None:
                    return self._users.get(uid).pop(provider)
        else:
            ...
        
    def _make_provider(self, uid, provider: str, data: dict):
        return self._make_user(uid, **{provider: data})

    # Abstraction Layers (for new users)
    def add(self, uid: str, provider: str | None = None, data: dict | None = None) -> dict | None:
        if provider is None or provider is None:
            return self._make_user(uid)
        return self._make_user(uid, **{provider: data})
    def remove(self, id: str) -> dict | None:
        return self._remove_user(id)
    
    # Abstraction Layers
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
    
    def to_save(self) -> dict:
        return {
            "str": self.__repr__(),
            "users": self.users,
            "amount": len(self.users),
            "save_file": self.save_file,
        }
    def to_save(self) -> dict:
        return {
            "users": self.users,
        }
    def __repr__(self) -> str:
        return "<UserManager>[User Count: {}]".format(len(self.users))

