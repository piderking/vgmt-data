from time import time
from abc import abstractmethod
from ..serialize import serialize
from ..saving import Saveable
from ...env import CONFIG
class Data():
    def __init__(self, **kwargs):
        self._data: list = kwargs.pop("data")
        self.params: dict = kwargs

    def to_dict(self, )->dict:
        return {"data":self._data, "param":self.params}
    
    
class EndpointData(Data): # General Endpoint Data
    def __init__(self,**kwargs:dict):
        """Endpoint Data
        
        Arguements:
            endpoint: (str) Endpoint's name
            increment: (int) Amount of second between each data 
            data: (list) Given data, timerseries
        """
        self.endpoint: str = kwargs.pop("endpoint")
        self.increment: int = int(kwargs.pop("increment"))
        super().__init__(**kwargs)
        
    @property
    def data(self) -> list:
        """

        Returns:
            list: _description_
        """
        return self._data
    def to_dict(self) -> dict:
        return dict(super().to_dict() | {"endpoint":self.endpoint, "increment":self.increment})
    def rip(self) -> list[any]:
        # Pull the data
        return self.data

class VGMTData(Saveable, EndpointData):
    increment: int
    def __init__(self,**kwargs:dict):
        """Endpoint Data
        
        Arguements:
            endpoint: (str) Endpoint's name
            increment: (int) Amount of second between each data 
            data: (list) Given data, timerseries
            Either:
                filename: (str) filename if loaded from a file
            Or:
                uid: (str) UID of user
                time: (dict) {year, day}
            
        """
        EndpointData.__init__(self, **kwargs) # Inherit sata

        self._data = list(zip(*  [kwargs.keys()] + check_any([value.rip() if type(value) is EndpointData else False for _, value in kwargs.items()])))
        
        Saveable.__init__(self, filename=kwargs.get("filename") if kwargs.get("filename") is not None else CONFIG._replace(CONFIG.data["file_structure"].replace("{uid}", kwargs["uid"]).replace("{day}", "{}-{}".format(kwargs["time"]["year"], kwargs["time"]["day"]))))
        
    def to_csv(self,) -> str:
        return str(self) + "\n" + "\n".join([",".join([serialize(r) for r in row]) for row in self._data])
    
    @classmethod
    def from_csv(cls, csvs: str, structure: list[type] = None):
        """Generate a VGMTData from a CSV file

        Args:
            csvs (str): csv string (raw)
            structure (list[type], optional): structure of datatype in csv, auto generates if not provided

        Returns:
            _type_: _description_
        """
        line = csvs.split("\n")[0]
        if structure is None:
            # get the first rows of datatypes
            structure = replace(csvs.split("\n")[2].split(","))
        return cls(
            data=[csvs.split("\n")[1]]+[structure[idx](row.split(",")) for idx, row in enumerate(csvs.split("\n")[2:])]     # first row is construction info, second is keys
        )
    def to_save(self):
        return self.to_csv() # no need to serialize
    
    @classmethod
    def from_csv(cls, **kwargs:dict):
        return cls(**kwargs)   
    
    def __add__(self, data: EndpointData | list) -> list[list]:
        if type(data) is EndpointData:
            self._data = [self._data[idx] + [row] for idx, row in enumerate(data.data)]
        elif type(data) is VGMTData:
            self._data = [self._data[idx] + row for idx, row in enumerate(data.data)]
        elif type(data) is list:
            self._data = [self._data[idx] + [row] for idx, row in enumerate(data)]
        return self.data
    def __repr__(self) -> str:
        "incr, {}, endpoints, {}".format(self.increment, ".".join(self.data[0]))
def check_any(vals: list):
    if all(vals):
        return vals
    else:
        raise ValueError("Value is supposed to be type EndpointData")
    

def replace(types: list[any]) -> list[type]:
    return [test(t) for t in types]

def test(t: any,) -> type:
    map = {
        "float":float,
        "int":int,
        "str":str,
        "bool":bool

    }
    for v in map.values():
        try:
            v(t)
            return v
        except ValueError:
            continue
        