from .log import info, warn
from .saving import Saveable
from time import time as ntime
class Action():
    def __init__(self, **data):
        """Create from dictionary
        kwargs: dict
        args: dict
        return: dict
        """
        self.data = data
    def to_dict(self):
        return self.data
    
    def to_display(self):
        print("Called")
        return {
            "args": {
                key:{
                    "value": self.args[key],
                    "type": type(self.args[key]).__name__
                } for key in self.args.keys()
            },
            "kwargs": {
                key:{
                    "value": self.kwargs[key],
                    "type": type(self.kwargs[key]).__name__
                } for key in self.kwargs.keys()
            },
            "return": {
                "value":self.data,
                "type": type(self.data).__name__,
            },"details":{
                "doc":self.doc,
                "name":self.name
            }
        }
    
    def __getattr__(self, attr):
        return self.data[attr]
    def __repr__(self) -> str:
        return "{}({}, {})->{}=({})".format(
            self.name,
            ",".join(["{}:{}={}".format(key, type(self.args[key]).__name__, self.args[key]) for key in self.args]),
            ",".join(["{}:{}={}".format(key, type(self.kwargs[key]).__name__, self.kwargs[key]) for key in self.kwargs]),
            self.treturn,
            type(self.treturn).__name__
        )

class ActionLogger(Saveable):
    max_size = 100
    actions: list[Action] = []
    def __init__(self, file_name: str= None, actions: list = [], time=None, max_size: int = 100, **kwargs) -> None:
        self.__qualname__ = "actions"
        
        super().__init__(file_name=file_name,)

        
        time = ntime() if time is None else time
        self.actions = [action if type(action) is Action else Action(**action) for action in actions]
        self.max_size = max_size
        info("Last time saved was... {} minutes ago".format((int(ntime())-int(time))/60), name=self.__qualname__, type="Action Logger")
        pass
    
    def append(self, action: Action) -> None:
        
        self.actions.append(action)
        if len(self.actions) > self.max_size:
            self.actions.pop(0)
    def to_dict(self) -> dict:
        return {
            "actions": self.actions,
            "max_size": self.max_size,
            "time": ntime()
        }
def log(action_logger: ActionLogger):
        """Verify all tokens in a function request

        Args:
            token_key (str, optional): special token only want to be verified in the kwargs
            
        """
        def decorator(function):
            def wrapper(*args, **kwargs):
                result = function(*args, **kwargs)
                function.__annotations__.pop("kwargs")
                function.__annotations__.pop("return")
                action_logger.append(Action(args=dict(list(zip(function.__annotations__.keys(), args))), kwargs=kwargs, treturn=result, doc=function.__doc__, name=function.__name__, ))
                return result
            return wrapper
        return decorator