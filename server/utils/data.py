from typing import Self
from server.utils.exceptions import IntervalError
import numpy as np

class DataModel(object):
    _type: type
    
    def __init__(self,**kwargs):
        self.data = kwargs
    
    def __getattr__(self, name: str) -> any:
        if self.data.get(name) is None:
            return self.__getattribute__(name)
        else:
            return self.data[name]
    def __setattr__(self, name:str, item: any):
        tem = self.data.pop(name, None)
        self.data[name] = item
        return tem
    def to_dict(self) -> dict:
        return self.data
    
type UID = str
type AcceptableData =  str | int | float | bool  | None
AcceptableDataType = [str, int, float, bool, None]
class CleanedDataModel(DataModel):
    uid: UID
    time: int
    data: list[dict[str, AcceptableData,]] # list of dictionaries with data values list[{"blood_sugar": 111}]
    values: dict
    interval: int
    
    def to_sorted(self):
        self.data.pop("uid")
        return SortedDataModel(**self.to_dict())
class SortedDataModel(DataModel):
    time: int
    data: list[dict[str, AcceptableData,]]
    values: dict
    _interval: int # minute interval
    
    
    def __init__(self, **kwargs):
        #data: list[dict[str, AceptableData,]] = kwargs.pop("data") # -> (["blood_sugar",], [111,])
        
        interval = kwargs.pop("interval", 5) # prevent from being added to "data"
        super().__init__(**dict(kwargs | {}) )
        self.interval = interval
        
    @property
    def interval(self) -> int:
        return self._interval  
    
    
    def set_interval(self, interval: int) -> Self:
        self.interval = interval
        return self
    @interval.setter
    def interval(self, interval: int):
        """
        Only valid to increase interval
        """
        if self.interval is None:
            self._interval = interval
            
        if self.interval == interval:
            return
        
        
        if interval > self.interval:
            adx = 0
            
            for key in self.data.keys():
                col = []
                for idx, data in enumerate(self.data[key]):
                    if idx*self.interval == (idx+adx)*interval:
                        col.append(data[idx+adx])
                    elif idx*self.interval - (idx+adx)*interval > interval:
                        adx += 1
                    else:
                        col.append(data[idx+adx])
                self.data = col
        else:
            raise IntervalError("{}: past > {}: new; when changing intervals".format(self.interval, interval))
    


