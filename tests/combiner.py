from server.data.fmt import EndpointData
from server.utils.data import CleanedDataModel, SortedDataModel, UID
from ..server.data.acceptor.sorter import DataAcceptorSorter, SortedStore
import threading 
from ..server.env import CONFIG
from ..server.utils.log import info
from concurrent.futures import ThreadPoolExecutor
import time
from ..server.worker.endpoint import users
import numpy as np

class DataAcceptorCombiner(threading.Thread):
    max_workers: int = 2
    data_sorter: DataAcceptorSorter
    @property
    def to_combine(self) -> SortedStore: # Readonly, doesn't make modifications
        return self.data_sorter.sorted
    @property
    def overflow(self) -> int:
        return self.data_sorter.overflow
    def __init__(self, data_sorter: DataAcceptorSorter | None, daemon: bool = True, auto_start: bool = False, max_workers: int = 2, overflow: int = 3):
        self.data_sorter  = data_sorter 
        self.daemon = daemon
        self.max_workers = max_workers
        self.data_sorter.overflow = overflow
        
        
        threading.Thread.__init__(self)

        if auto_start or bool(CONFIG.THREAD["auto_start"]): self.start() # s

    def combine(self, data: dict[UID, list[SortedDataModel]]) -> ...:  
        for uid, user_data in data.items():
            cols = user_data[0].data[0].keys() # keys  
            # interval updated 
            new_data: list[SortedDataModel] = [ item.set_interval(user_data[0].interval) for item in user_data]
            
            # propigate inital start (lowest out of all) # TODO optimize this
           
            
            
            users.get(uid)
    def process(self, executor: ThreadPoolExecutor, batch: list[dict[UID, list[SortedDataModel]]]) -> None:
        self._final.extend(executor.map(self.combine, *[batch]))         
    
    def run(self):
        while self.is_alive():
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                if len(self.to_combine.keys()) > 0:
                    self.process(executor, self.data_sorter.get(multi=self.overflow))

                    # self.responses = self.responses[:taking]
                else:
                    # Isn't needed and will stop boggling the system and sleep for 1/4 of second
                    time.sleep(CONFIG.THREAD["time_out"]) # TODO add customizability to timeing in confi
        info("Thread Killed", _type="DataAcceptor", name="Cleaner")
        
    
    def start(self) -> None:
        return super().start()