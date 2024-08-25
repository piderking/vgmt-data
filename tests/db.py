from typing import Any


class Query():
  def __init__(self, **kwargs) -> None:
    self.target=kwargs.pop("target") # Get the "target"
    self.params = kwargs


  

class db(object):
  def __init__(self,keys: dict = None, **kwargs: dict):
    self.keys = dict({
      "*":"__all__",
    } | keys if keys is not None else {})
    self._data = kwargs
    pass
  @property
  def data(self) -> dict:
    return self._data
  def __getattr__(self, name):
    return self._data.get(name)
  def query(self, query: Query):
    attr = self.__getattr__(query.target)
    
    
        
    attr 
  def cypher(self, query: str):
    for key in self.keys.keys():
      query = query.replace(key, self.keys[key](passed=key))
    return query
  def __all__(self, *args: list, passed: str="*"): # Get all the keys
    if len(args) == 0:
      return set(self._data.keys())
    _all = []
    for arg in args:
      if hasattr(arg, "__dict__"):
        _all.extend(arg.__dict__)
      else:
        if type(arg) is dict:
          _all.append(arg)
        else:
          _all.extend(arg)
    return _all
  def __add__(self, other):
    ...
    

print(db().__all__(Query(target="sdfsdf", key="sdfsd")))
print(db().__all__(["dsfsd"], {"sfsdf":"sdfsd"}))