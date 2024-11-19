from datetime import datetime
import itertools
import math
from typing import Any, Literal, Self
import os
from ...utils.exceptions import IntervalError
from ...utils.list import position_at, transform
from ...utils.step import step
from ...data.web import DataResponse
from ...utils.data import CleanedDataModel, SortedDataModel, UID, AcceptableData, AcceptableDataType
from ...utils.types import VALID_CSV_STRING
type TableDataEntry = dict[UID, AcceptableData]
type TableData = list[TableDataEntry]
import csv
type Interval = int

class Row():
    data: list[AcceptableData] = []
    labels: list[str] = []
    time: int
    
    @classmethod
    def from_sorted_data_model(cls, sorted_data_model:SortedDataModel, interval:int = None):
        # TODO transform sorted data model into a Row(s) model
        # if multiple colms in sorted data model than have it become a list of Row object
        if interval: sorted_data_model.interval = interval 
        return [cls.__init__(
                time=sorted_data_model.time + idx*sorted_data_model.interval,
                labels=list(tdict.keys()),
                data=list(tdict) # get only vlaues

            ) for idx, tdict in enumerate(sorted_data_model.data)]
    
    def __init__(self, **kwargs: dict[str, list[str] | list[AcceptableData]]):
        self.time = kwargs.get("time")
        self.data.extend(kwargs.get("data", []))
        self.labels.extend(kwargs.get("labels", [None for _ in self.data]))
        
        
        
    def __repr__(self):
        return ",".join(self.data)
    def validate(self):
        return all([type(entry) in AcceptableDataType for entry in self.data])
    
class Col():
    name: str
    _interval: Interval
    data: list[AcceptableData]
    def __init__(self, time: int, name: str, interval: Interval, data: list[AcceptableData]):
        self.name = name
        self.data = data
        self.time = time # inital start time
        self._interval = interval 

    @property
    def interval(self) -> Interval:
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
                        col.append(data[idx+adx] if len(data) < idx+adx else None)
                    elif idx*self.interval - (idx+adx)*interval > interval:
                        adx += 1
                    else:
                        col.append(data[idx+adx] if len(data) < idx+adx else None)
                self.data = col
        else:
            raise IntervalError("{}: past > {}: new; when changing intervals".format(self.interval, interval))

        
        # move time to the appropriate time stamp
        #if self.time % self.interval > 0:
        times = math.floor(self.time / self.interval) # number of intervals in the time variable

        # if the precent error is greater than 10% then move to the nearest point
        if (self.time - self.interval*times) / self.interval*times > (10 / 100): 

            # if distance between next increment is bigger than the drop to the next inference then just go down to the next increment
            self.time += (-1 if abs(self.time - self.interval * times) > abs(self.interval * times - self.time) else 1) * (self.time % interval) 
        
        
        self.time = self.interval * times # just go to the nearest floored value
        
# Rows & Cols
type Rows = list[Row]  
type Cols = list[Col]

# Values (special one time values)
type Values = dict[Label, AcceptableData]

# Label (ex: blood_sugar, time, ...)
type Label = str

# 
type uCol = list[list[AcceptableData]]
type uRow = list[list[AcceptableData]]

class TableResponse():
    time: int 
    interval: Interval # amount of minutes / per row
    _cols: list[Label] = [
        "time", "blood_sugar", "hr",
    ]
    _data: list[list[AcceptableData]] = [
        
    ]
    _values: Values = {
        
    }
    
    
    @classmethod
    def is_acceptable_value(cls, value: str) -> AcceptableData | bool:
        return value if value in AcceptableDataType else False
        
    @property
    def values(self,) -> Values:
        return self._values
    
    @values.setter
    def values(self, values:Values ):
        self._values = dict(self._values | {values})
        
    def to_list(self) -> uCol: # Get Full Table Values
        return [self._cols] + self._data
    
    @property
    def rows(self) -> Rows:
        return [Row(data=row, labels=self.cols, time=self.time + idx * self.interval) for  idx, row in enumerate(self._data)]
    
    
    def get_labels(self, rows: list[Label] = None) -> tuple[list[Label], Rows]:
        if rows:
            sort = sorted([ position_at(rows, row_label) or 0 for row_label in rows])
            return [self.cols[place] for place in sort],  transform(itertools.filterfalse(lambda x: not all(x), [ x if i in sort else None for i, x in enumerate(zip(*sort))]))
        
        return [self._cols, self._data]
    @property
    def cols(self) -> Cols:
        return [Col(col, name=self._cols[idx]) for idx, col in enumerate(zip(*self.data))]
    @cols.setter
    def cols(self, new_label: Label | list[Label]) -> None:
        self.cols = self._cols + new_label if type(new_label) is list else [new_label]
        
        # transform into a list
        new_label = [None for _ in [[str(new_label)] if type(new_label) is str else new_label]]
        
        for idx, _ in enumerate(self._data):
            self._data[idx] = self._data[idx] + new_label
        
        
        
        
    
    @property
    def data(self) -> uRow:
        return self._data
    
    def get_col(self, col_name:str, for_index: bool = False) -> Col | None:
        for idx, col in enumerate(self.cols):
            if col.name == col_name: return col if not for_index else idx
        return None
    def get_row(self, index: Interval) -> Row | None:
        return Row(data=self._data[index] if len(self._data) - 1 > index else None, labels=self.cols, time=self.time + index * self.interval )   
    
    def __add__(self, new: Row | Col | Rows | Cols | SortedDataModel):
        if type(new) is  SortedDataModel:
            # sorted data model is rows of time incremements
            self + Row.from_sorted(new)
            
        if type(new)  is list:
            for mew in new: 
                    
                self + mew
                
        else:
            if type(new) is Col:
                # set interval (make it to the larger interval)
                if self.interval > new.interval:
                    self.interval = new.interval
                else:
                    new.interval = self.interval
                
                
                # find inital interval
                if new.time < self.time: # starts before
                    self._data = [[None for _ in self.cols] for _ in range( math.floor(( self.time - new.time ) / self.interval) )] + self.data
                    self.time = new.time
                if new.time + new.interval * len(self.data) > self.time + self.interval * len(self.data): # range goes afterwards
                    self._data = [[None for _ in self.cols] for _ in range( math.floor(( new.time - self.time) / self.interval) )] + self.data
                
                # check cols exsist
                if not new.name in set(self.cols): self.cols = new.name
                
                # combine the data
                place = math.floor((self.time - new.time) / self.interval)
                
                # add the data once gotten to the certain threshold (place) and once past the entire list then it can take only the row again
                self._data = [row + [new.data[ ridx - place]] if ridx >= place and ridx < place + len(new.data) else row  for ridx, row in self.data] 
                ...
            elif type(new) is Row:
                # check valid
                if not new.validate(): raise TypeError("Found a data type not allowed in AcceptableDataTypes! Erroring")
                
                # check for time range
                if self.time + len(self.data) * self.interval > new.time:
                    if new.time < self.time:
                        self._data = [[None for _ in self.cols] for _ in range( math.floor(( self.time - new.time ) / self.interval) )] + self.data
                        self.time = new.time
                else:
                    self._data = [[None for _ in self.cols] for _ in range( math.floor(( new.time - self.time) / self.interval) )] + self.data
                
                iten = []
                # check for cols now
                for col in Row.col: 
                    # instead of using "in" because it already has a complexity of O(n) and we'll have to look for it anyways
                    for idx, main_col in enumerate(self.cols):
                        
                        if col == main_col:
                            iten.append(idx)
                        if idx == len(self.cols) - 1:
                            iten.append(None)
                
                for idx, label in enumerate(iten):
                    if label is None:
                        # add labels and creates new cols
                        self.cols = new.labels[idx]
                        
                        iten[idx] = len(self.cols) - 1
                    
                place = math.floor((self.time - new.time) / self.interval)
                
                # has to exssit
                #self._data[place] = [None for _ in self.cols]
                
                for idx, item in enumerate(iten): self._data[place][item] = new.data[idx]
                
                
                ...
    def __init__(self, *args, time: int):
        #data = data
        self.time = time
        
        for arg in args:
            self + arg
        
        
    
    def select_important(self, data: list[tuple[str, str | None, str | None, str | None]]) -> dict: 
       # Stepped Keys, id, type, trans
       
       
        return {
            isImpt: (path, hasType, hasTrans) for path, isImpt, hasType, hasTrans in list(itertools.filterfalse(lambda t: True if t[1] is None else False, data)) # transform into dict
        }
    
    
    @classmethod
    def transform(cls, data: any, trans: Literal["int", "str", "time", "float"]) -> Any | str:
        tp = {
            "int": int,
            "str": str,
            "time": lambda t: datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").timestamp(),
            "float": float,
            
        }
        return tp[trans](data) if tp.get(trans) is not None else str(data)
    
    @classmethod
    def transform_any(cls, data: Any) -> AcceptableData:
        for t in AcceptableDataType:
            if t is None:
                continue
            try:
                return t(data)
                
            except:
                continue
        
    @classmethod
    def step(cls, val: dict, keys:list[str] | str, trans: str): # i love recursive
        keys = keys.split(".") if type(keys) is str else keys
        if len(keys) == 1:

            return cls.transform(val.get(keys[0]), trans)
        
        elif type(val) is dict:
            key = keys.pop(0)
            if val.get(key) is None:
                return None
            
            if len(keys) == 1:
                return [cls.transform(t.get(keys[0]), trans) for t in val[key]]
            elif len(keys) > 1:
                return step(val[key], keys) 
        return val # defaulkts
    
    @classmethod
    def clean(cls, data: DataResponse) -> CleanedDataModel:
        # data.format, data.data
        ret = {
                isImpt: cls.step(data.data, path, trans) for isImpt, (path, _, trans) in cls.select_important(data.format).items()
           }
        
        return CleanedDataModel(**{
           "uid": data.uid,
           "time": data.time, #  start time of data
           "data": { # only values that are lists
                key: ret.get(key) for key in list(itertools.filterfalse(lambda key: not type(ret.get(key)) is list, ret.keys()))    
           },
           "values": {
                key: ret.get(key) for key in list(itertools.filterfalse(lambda key: type(ret.get(key)) is list, ret.keys()))    

           }
           # if element is a value (not a holder) it'll be expressed as the value
           # if a holder it'll be a list of the values in a row
        })
    
    @classmethod
    def from_csv(cls, path: os.PathLike = None, string: str = VALID_CSV_STRING) -> Self: