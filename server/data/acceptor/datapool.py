from typing import Any
from ...utils.exceptions import WritingReadOnlyDataPool
class Object: ...
class DataPool[T]():
           
        
    def __init__[T](self, pool_obj: Object, pool: str = "responses", read_only: bool = False, append: bool = True) -> None:
        self.pool_obj = pool_obj
        self.pool = pool
        self.read_only = read_only
        self.append = append
    
    @property
    def data(self) -> T:
        return getattr(self.pool_obj, self.pool)
    @data.setter
    def data(self, new_value) -> T:
        return self + new_value
    
    def __add__(self, new_value) -> T:
        if self.read_only:
            raise WritingReadOnlyDataPool("Writing to a read only datapool")
        
        if self.append:
            setattr(self.pool_obj, self.pool, getattr(self.pool_obj, self.pool) + new_value if type(new_value) is list else [new_value])
        else:
            setattr(self.pool_obj, self.pool, new_value if type(new_value) is list else [new_value])

        return self.data