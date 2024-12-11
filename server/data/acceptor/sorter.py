from server.data.fmt import EndpointData
from server.utils.data import CleanedDataModel, SortedDataModel, UID
from .cleaner import DataAcceptorCleaner
import threading 
from ...env import CONFIG
from ...utils.log import info, warn
from concurrent.futures import ThreadPoolExecutor
import time
from ...worker.endpoint import users
from .datapool import DataPool
import random
from .table import TableResponse
from ..saving.save import save_table


type SortedStore = dict[UID, list[SortedDataModel]]

class DataAcceptorSorter(threading.Thread):
    max_workers: int = 2
    data_cleaner: DataAcceptorCleaner
    pool: DataPool[list[SortedDataModel]] 
    _sorted: SortedStore
    overflow: int = 3
    
    
    
    metadata: dict[UID, dict[str, int | str]] = {}
    tables: dict[UID, TableResponse] = {}
    

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
        if self._sorted.get(cleaned.uid) is None: 
            self.metadata[cleaned.uid] = {
                "last_used": time.time(),
                "table_alive": False
                # size of non tabled data
            }
            self.tables[cleaned.uid] = None #  TableResponse(time=cleaned.time,)
            
            # table.check_sourced
            self._sorted[cleaned.uid] = []
            
        self._sorted[cleaned.uid].append(cleaned.to_sorted())
        
        
        #return self._sorted
    def take_sorted(self, uid: UID) -> list[SortedDataModel]:
        return self._sorted.pop(uid) # pop the data
    def __init__(self, data_cleaner: DataAcceptorCleaner | None, daemon: bool = True, auto_start: bool = False, max_workers: int = 2):
        self.data_cleaner = data_cleaner or DataAcceptorCleaner(daemon=daemon, auto_start=auto_start, max_workers=max_workers)
        self.cut_size = data_cleaner.cut_size # sync cut_size
        self.max_workers = max_workers
        
        self.pool = DataPool(self.data_cleaner, "_final")
        
        
        
        threading.Thread.__init__(self)
        self.daemon = daemon

        if auto_start or bool(CONFIG.THREAD["auto_start"]): self.start() # s

    def create_table(self, uid: str) -> TableResponse:
        if self.sorted.get(uid) and self.metadata.get(uid):
            if not self.metadata[uid]["table_alive"]:
                self.tables[uid] = TableResponse(time.time()) # set time to now, new data will change the time
            self.tables[uid] = self.tables[uid] + self.take_sorted(uid)
            self.metadata[uid] = dict(self.metadata[uid] | {
                "last_used":time.time(),
                "table_alive": True
            })
                
            return  self.tables[uid]
    def save(self, uid: UID):
        
        
        if self.metadata.get(uid) and self.metadata[uid]["table_alive"]:
            self.create_table(uid)
        
            self.tables[uid] = self.tables[uid].check_sources(uid)
            
            tbl = self.tables.pop(uid)
            save_table(tbl, uid, tbl.time, overwrite=True) # check_sources is run before so we can run itr

            self.tables[uid] = None

            self.metadata[uid] = dict(self.metadata[uid] | {
                "last_used":time.time(),
                "table_alive": False
            })
        
        
    def join(self, t: int = None) -> None:
        while len(self.data_cleaner._final ) > 0 or len(self.data_cleaner.responses) > 0: # Check Data Cleaner object to be empty
            pass
        
        for uid in self._sorted.keys():
            # convert to table & save
            self.save(uid)
        
        super(self).join(t) 
    @property
    def data(self,):
        """
        Data to be proccessed
        """
        return self.data_cleaner.final # cuts from source
    
    
    def sort(self, data: CleanedDataModel):
        #users + data
        self.sorted = data
        ...
        
    
    def check_user(self, uid: UID):
        if self.sorted.get(uid):
            ...
        else:
            return False
    
    def process(self, executor: ThreadPoolExecutor, batch: list[CleanedDataModel], func) -> None:
        self._final.extend(executor.map(func, *[batch]))         
    
    def execute(self, executor: ThreadPoolExecutor):
        if len(self.data_cleaner._final) > 0:
    
            #taking = len(self.responses) - self.cut_size if len(self.responses) > self.cut_size else 0
            self.process(executor, self.data_cleaner.final, self.sort)
            return True
        else: # skip this itteration
            return False
    def run(self):
        info("Starting Sorting Server for Datapool")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while self.is_alive() and executor:
                if self.data_cleaner.execute(executor) and self.execute(executor):
                    ...
                else:
                    # place holder values
                    MAXIMUM_ITEMS = 5
                    self.process(executor, [k for k, i in self.sorted.items() if len(list(i)) >= MAXIMUM_ITEMS], self.save)

                    # isn't needed -- process service threads
                    
                    # Isn't needed and will stop boggling the system and sleep for 1/4 of second
                    time.sleep(CONFIG.THREAD["time_out"]) # TODO add customizability to timeing in confi
        info("Thread Killed", _type="DataAcceptor", name="Cleaner")
        
    
    def start(self) -> None:
      
        return super().start()