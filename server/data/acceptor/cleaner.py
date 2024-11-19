from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time
from typing import Any, Literal

from server.utils.data import CleanedDataModel, DataModel
from server.utils.step import step
from ..web import DataResponse
import threading
import itertools
from ...env import CONFIG
from ...utils.log import info

from ...utils.log import info, debug, warn




class DataAcceptorCleaner(threading.Thread):
    responses: list[DataResponse] = [] # TODO add loading saving functionality    
    _final: list[CleanedDataModel] = []
    max_workers: int = 2
    cut_size: int = 3
    def __init__(self, responses: list[DataResponse], daemon: bool = True, auto_start: bool = False, max_workers: int = 2) -> None:
        self.responses = responses or self.responses
        
        threading.Thread.__init__(self)
        
        self.max_workers = max_workers
        self.daemon = daemon
        if auto_start or bool(CONFIG.THREAD["auto_start"]): self.start() # s
    
    def select_important(self, data: list[tuple[str, str | None, str | None, str | None]]) -> dict: 
       # Stepped Keys, id, type, trans
        return {
            isImpt: (path, isType, isTrans) for path, isImpt, isType, isTrans in list(itertools.filterfalse(lambda t: True if t[1] is None else False, data)) # transform into dict
        }
                
    @property        
    def final(self) -> list[CleanedDataModel]:
        taking = len(self._final) - self.cut_size if len(self._final) > self.cut_size else 0
        
        temp = self._final[taking:]
        self._final = self._final[:taking]
        
        return temp
    
    def clean(self, data: DataResponse) -> dict:
        # data.format, data.data
        ret = {
                isImpt: self.step(data.data, path, trans) for isImpt, (path, _, trans) in self.select_important(data.format).items()
           }
        
        return CleanedDataModel(**{
           "uid": data.uid,
           "time": data.time, # TODO start time of data
           "data": { # only values that are lists
                key: ret.get(key) for key in list(itertools.filterfalse(lambda key: not type(ret.get(key)) is list, ret.keys()))    
           },
           "values": {
                key: ret.get(key) for key in list(itertools.filterfalse(lambda key: type(ret.get(key)) is list, ret.keys()))    

           }
           # if element is a value (not a holder) it'll be expressed as the value
           # if a holder it'll be a list of the values in a row
        })
        
        
    
    def process(self, executor: ThreadPoolExecutor, batch: list[DataResponse]) -> None:
        self._final.extend(executor.map(self.clean, *[batch])) 
    
    @staticmethod
    def transform(data: any, trans: Literal["int", "str", "time", "float"]) -> Any | str:
        tp = {
            "int": int,
            "str": str,
            "time": lambda t: datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").timestamp(),
            "float": float,
            
        }
        return tp[trans](data) if tp.get(trans) is not None else str(data)
        
    def step(self, val: dict, keys:list[str] | str, trans: str): # i love recursive
        keys = keys.split(".") if type(keys) is str else keys
        if len(keys) == 1:

            return DataAcceptorCleaner.transform(val.get(keys[0]), trans)
        
        elif type(val) is dict:
            key = keys.pop(0)
            if val.get(key) is None:
                return None
            
            if len(keys) == 1:
                return [DataAcceptorCleaner.transform(t.get(keys[0]), trans) for t in val[key]]
            elif len(keys) > 1:
                return step(val[key], keys) 
        return val # defaulkts
        
    def run(self):
        info("Starting Sorting Server for Datapool")

        while self.is_alive():
            with ThreadPoolExecutor(max_workers=1) as executor:
                if len(self.responses) > 0:
                    
                    taking = len(self.responses)- self.cut_size if len(self.responses) > self.cut_size else 0
                    self.process(executor, self.response[taking:])
                    
                    self.responses = self.responses[:taking]
                else:
                    # Isn't needed and will stop boggling the system and sleep for 1/4 of second
                    time.sleep(CONFIG.THREAD["time_out"]) # TODO add customizability to timeing in confi
        info("Thread Killed", _type="DataAcceptor", name="Cleaner")
        