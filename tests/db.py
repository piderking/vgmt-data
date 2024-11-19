import itertools
import math
from time import time
from typing import Self, Union
import pandas as pd
from server.utils.data import CleanedDataModel

type Record = Union[float, str, int, None]
type Row = list[Record]
type Col = list[Record]
type Key = str

columns = ["time", "blood_sugar", ] # TODO add all labels here
class DataDB():
    # number of seconds
    increment: int = 5*60 # 5 minutes increments
    inital_time = None

    
   
    _data: dict[Row] = {
        "blood_sugar": [
            
        ]
    }
    

    @property
    def col(self) -> list[Key]:
        return list(self._data.keys())
    def __add__(self, data: CleanedDataModel | list) -> Self:
        """Compound Data into single source

        Args:
            data (CleanedDataModel | list): _description_

        Returns:
            Self: _description_
        """
        if type(data) is CleanedDataModel:
             if not math.floor(int(data.time) % self.increment) == 0:
                data.time -= (int(data.time) % self.increment) # go to nearest increment
                
                heads = list(data.data.keys())
                for key in list(itertools.filterfalse(lambda x: x[1] in self.col, enumerate(heads))): 
                    if self._data.get(key, None) is None:
                        self._data[key] = []
                    
                    # pre-data col (adds inital None to make them the same length to either front/back)
                    # add time exsists before the new col
                    self._data[key] = self._data[key] + [ None for _ in range(round( data.time - self.inital_time  ) / self.increment ) ] if data.time > self.inital_time else []
                    
                    # add time after  
                    self._data[key] =  [ None for _ in range(round( self.inital_time - data.time ) / self.increment ) ] if data.time  < self.inital_time else [] + self._data[key]

                    
                    # calculate pre
                    """
                    calculations
                    
                    pre:
                    
                    new = len(2), start time 5
                    old = len(5)   start time 8
                    
                    to balance we need 
                    pre:
                    start = 7sudo
                    [old, old, old, old, old]
                    
                    to_add:
                    start = 5
                    [new, new]
                    
                    combine
                    start = 5
                    [new, new, None, old, old, old, old, old]
                    """
                    # left side is for newser data, right side is for older data being added
                    self._data[key] = list( [] + [] + [] ) if data.time > self.inital_time else list([] + [] + [])

                    """
                    calculations
                    
                    pre:
                    
                    new = len(2), start time 8
                    old = len(3)   start time 3
                    
                    to balance we need 
                    pre:
                    start = 5
                    [old, old, old]
                    
                    to_add:
                    start = 3
                    [new, new]
                    
                    combine
                    start = 3
                    [old, old, old, None,  None, new, new]
                    """
                    
                    
                    # DataWriting (pefer new)
                    if data.data.get(key): # check that refrence exsists
                        
                        # if 
                        t = round( self.inital_time - data.time ) / self.increment
                        
                        if data.time < self.inital_time:
                            new = []
                            for idx, record in enumerate(data.data[key]):
                                if len(data.data[key] - idx > 0):
                                    new.append(data.data[key][idx])
                                else: 
                                    new.append(record)
                        else:
                            new = []
                            for idx, record in enumerate(data.data[key]):
                                if idx*self.increment+self.inital_time > data.time:
                                    if len(data.data[key]) - math.floor((data.time-self.inital_time+idx*self.increment)/self.increment) > 0:
                                        new.append(data.data[key][(data.time-self.inital_time+idx*self.increment)/self.increment])
                                else:
                                    new.append(record)


                        for idx, record in enumerate(data.data[key]):
                            if data.time < idx*self.increment + self.inital_time:
                        #self._data[key] = [record if self.inital_time+idx*self.increment > data.time else ( data.data[key][idx-t] if (data.time - (self.inital_time+idx*self.increment))/self.increment   else record) for idx, record in enumerate(self._data)] 
                    """
                    Do Both
                    
                    Newer Data:
                    1,    2,     3,    4,
                    current, None, None, new
                    
                    Older Data:
                    
                    jnew, None, None, current
                    
                    Xing
                    
                    current, current, current-> new, new 
                    
                    Pre-Xing
                    new, new, current->new, current
                       
                    
                    
                    
                    """

                    # add col data                
        """
        
            if type(data) is CleanedDataModel:
                # TODO make increments work in half times
                if not math.floor(int(data.time) % self.increment) == 0:
                    data.time - int(data.time) % self.increment # go to nearest increment 
                    
                heads = list(data.data.keys())
                not_present = list(itertools.filterfalse(lambda x: x[1] in heads, enumerate(heads)))
                self._col.extend([key for idx, key in not_present])
                self._data = [row.extend([None for _ in not_present]) for row in self._data]
                
                
                # present = list(itertools.filterfalse(lambda x: not x[1] in heads, enumerate(heads)))
                gen_data = {
                    key: self.correct_increment(val) for key, val in data.data
                } # correct messed up interval here
                #gen_rows: list[Row] = list( zip(*[gen_data[col] if col in heads else None for col in self._col]) )
                #valued = zip(*[data.data[col] for col in self._col]) 
                #self._data = [row if data.time < idx*self.increment else self.merge_rows(row, gen_rows(idx)) for idx, row in enumerate(self._data)]
                self._data.extend(
                
                )
                def merge_rows(self, inital: Row, merge: Row) -> Row:
        return inital
        """
            
        return self     
    
    def correct_increment(self, col: Col) -> Col:
        add_index = 0
        
        new_interval = round(col[1] - col[0] / 60) # round to nearest minute

        new_col = []
        if abs((self.increment-new_interval)/new_interval) > 0.1:
            # fix interval
            for idx, _ in enumerate(self._data): # change from stopping point
                if idx*self.increment == (idx+add_index)*new_interval:
                    new_col.append(col[idx+add_index])
                elif idx*self.increment - (idx+add_index)*new_interval > new_interval:
                    add_index += 1
                else:
                    new_col.append(col[idx+add_index])

                    
        return col

        
    def __del__(self, time_stamp: int):
        
        ...
    def __call__(self, ) -> EndpointData:
        pass
    