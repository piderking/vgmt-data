import os
from ..toml import CONFIG
from abc import abstractmethod
from .exceptions import SavingError, LoadingError
import json

class Saveable(object):
    def __init__(self, file_name: str | None = None)->  None:
        
        file_name = "<config_path>/" + self.__qualname__ + ".json" if file_name is None else file_name 
        self.file_name = CONFIG._replace(file_name)
        self.__name__ = str(file_name.split("/")[:-1]).split(".")[0]
        to_save.append(self)
    
    @classmethod
    def load(cls, file_name: str | None = None): 
        try:
            file_name = file_name if file_name is not None else CONFIG.USERS["file_path"]
            file_name = CONFIG._replace(file_name)
            if os.path.exists(file_name):
                loaded: dict = json.loads(
                        open(CONFIG._valid_directory(file_name), "r").read()
                    )

                return cls(
                    **dict(loaded | {
                        "file_name": file_name
                        }), # Can be changed in subclassing
                )
            else:
                return cls()
        except json.JSONDecodeError as e:
            raise LoadingError(e.msg)
    def save(self): 
        try:
            open(CONFIG._valid_directory(self.file_name), "w").write(json.dumps(
                self.to_save()
            ))
            return self.file_name
        except OSError:
            raise SavingError("Failed to save @path::{}\t @infered::{}".format(self.file_name, CONFIG._valid_directory(self.file_name)))
    
    @abstractmethod
    def to_save(self) -> dict[str, any]:
        return dict({
            
        })

        
to_save: Saveable = [] 
