from time import time
from abc import abstractmethod
from ..serialize import serialize
from ..saving import Saveable

class Data():
    def __init__(self, **kwargs):
        self.time = time()
        self._data = kwargs.pop("data")
        self.params = kwargs

    def to_dict(self, )->dict:
        return self._data
    @property
    def data(self) -> list:
        return self._data
class EndpointData(Data): # General Endpoint Data
    def __init__(self,**kwargs:dict):
        self.endpoint = kwargs.pop("endpoint")
        super().__init__(**kwargs)

    def rip(self):
        # Pull the data
        return self.data

class VGMTData(Saveable, EndpointData):
    increment: int = 5 # 5 minute incremments
    def __init__(self,filename: str = None, **kwargs:dict):
        super(EndpointData).__init__(**kwargs) # Inherit sata

        self.increment = kwargs.pop("increment")
        self._data = list(zip(*  [kwargs.keys()] + check_any([value.rip() if type(value) is EndpointData else False for _, value in kwargs.items()])))
        super(Saveable).__init__(filename=filename)
        
    def to_csv(self,) -> str:
        return str(self) + "\n" + "\n".join([",".join([serialize(r) for r in row]) for row in self._data])
    def to_save(self):
        return self.to_csv() # no need to serialize
    
    @classmethod
    def from_csv(cls, **kwargs:dict):
        return cls(**kwargs)   
    
    def __add__(self, data: EndpointData) -> None:
        self._data = [row + [data._data[idx]] for idx, row in enumerate(self._data)]
        
    def __repr__(self) -> str:
        "incr, {}, endpoints, {}".format(self.increment, ".".join(self.data[0]))
def check_any(vals: list):
    if all(vals):
        return vals
    else:
        raise ValueError("Value is supposed to be type EndpointData")