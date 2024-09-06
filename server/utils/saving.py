import os
from ..toml import CONFIG
from abc import abstractmethod
from .exceptions import SavingError, LoadingError, SerializeError
import json
from .serialize import serialize
from ..utils.log import info
class Saveable(object):
    def __init__(self, file_name: str | None = None)->  None:
        self.save_amt = 0
        file_name = "<config_path>/" + self.__qualname__ + ".json" if file_name is None else file_name 
        print("Filename is ", file_name)
        self.file_name = CONFIG._replace(file_name)
        self.__name__ = str(file_name.split("/")[:-1]).split(".")[0]
    
    @classmethod
    def load(cls, file_name: str | None = None): 
        try:
            file_name = file_name if file_name is not None else CONFIG.USERS["file_path"]
            file_name = CONFIG._replace(file_name)
            if os.path.exists(file_name):
                info("Loaded file...{}".format(file_name))
                loaded: dict = json.loads(
                        open(CONFIG._valid_directory(file_name), "r").read()
                    )
                return cls(
                    **dict(loaded | {
                        "filename": file_name,
                        }), # Can be changed in subclassing
                )
               
                
                
            else:
                info("Couldn't load file... {}".format(file_name))
                return cls(
                    **{"file_name":file_name}
                )
        except json.JSONDecodeError as e:
            raise LoadingError(e.msg)
    def save(self): 
        try:
            self.to_save()
            open(CONFIG._valid_directory(self.file_name), "w").write(json.dumps(
                self.to_save()
            ))
            return self.file_name
        except OSError:
            raise SavingError("Failed to save @path::{}\t @infered::{}".format(self.file_name, CONFIG._valid_directory(self.file_name)))
    
    @abstractmethod
    def to_dict(self) -> dict:
        ...
    def serialize(self, **data: dict) -> dict:
        for key, value in data.items():
            if type(value) is dict:
                data[key] = self.serialize(**value)
            if type(value) is list:
                data[key] = list(self.serialize(**{str(idx):x for idx, x in enumerate(value)}).values())
            elif hasattr(value, "to_dict"):
                data[key] = self.serialize(**value.to_dict())
            # default to nothing
        return data
    
    def to_save(self) -> dict[str, any]:
        return self.serialize(**self.to_dict())

        
