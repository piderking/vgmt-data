from server.data.fmt import EndpointData
from server.utils.data import CleanedDataModel, SortedDataModel, UID
from .cleaner import DataAcceptorCleaner
import threading 
from ...env import CONFIG
from ...utils.log import info, warn
from concurrent.futures import ThreadPoolExecutor
import time
from ...worker.endpoint import users
import random


type SortedStore = dict[UID, list[SortedDataModel]]

class DataAcceptorSorter(threading.Thread):
    max_workers: int = 2
    data_cleaner: DataAcceptorCleaner
    
    _sorted: SortedStore
    overflow: int = 3

    

    def get(self, key: UID = None, multi: bool | int = False) -> list[ list[ SortedDataModel ]] | list[ SortedDataModel ]:
        if key is None:
            key = list(random.shuffle(list(self.sorted.keys())))[(multi - ( len(self.sorted.keys()) if len(self.sorted.keys()) - multi < 0 else 0) ):]
            return [self.get(_key) for _key in key]
        return self._sorted.pop(key)

        
    @property
    def sorted(self) -> SortedStore:
        return self._sorted
    @sorted.setter
    def sorted(self, cleaned:CleanedDataModel) -> SortedStore:
        if self._sorted.get(cleaned) is None: self._sorted[cleaned.uid] = []
        self._sorted[cleaned.uid].append(cleaned.to_sorted())
        
        return self._sorted
    
    def __init__(self, data_cleaner: DataAcceptorCleaner | None, daemon: bool = True, auto_start: bool = False, max_workers: int = 2):
        self.data_cleaner = data_cleaner or DataAcceptorCleaner(daemon=daemon, auto_start=auto_start, max_workers=max_workers)
        self.cut_size = data_cleaner.cut_size # sync cut_size
        self.max_workers = max_workers
        
        
        
        threading.Thread.__init__(self)
        self.daemon = daemon

        if auto_start or bool(CONFIG.THREAD["auto_start"]): self.start() # s

    @property
    def data(self,):
        """
        Data to be proccessed
        """
        return self.data_cleaner.final # cuts from source
    
    
    def sort(self, data: CleanedDataModel):
        #users + data
        self.cleaned = data
        ...
        
    def process(self, executor: ThreadPoolExecutor, batch: list[CleanedDataModel]) -> None:
        self._final.extend(executor.map(self.sort, *[batch]))         
    
    def run(self):
        info("Starting Sorting Server for Datapool")
        while self.is_alive():
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                if len(self.data_cleaner._final) > 0:
                    
                    #taking = len(self.responses) - self.cut_size if len(self.responses) > self.cut_size else 0
                    self.process(executor, self.data_cleaner.final)
                    
                    # self.responses = self.responses[:taking]
                else:
                    # Isn't needed and will stop boggling the system and sleep for 1/4 of second
                    time.sleep(CONFIG.THREAD["time_out"]) # TODO add customizability to timeing in confi
        info("Thread Killed", _type="DataAcceptor", name="Cleaner")
        
    
    def start(self) -> None:
        if not self.data_cleaner.is_alive():
            self.data_cleaner.start()
        return super().start()