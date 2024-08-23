def dec(key: str):
    def decorator(function):
        def wrapper(*args, **kwargs):
            self: MyClass = args[0]
            print("{} is {}".format(key, self.__getattribute__(key)))
            result = function(*args, **kwargs)
            return result
        return wrapper
    return decorator
class MyClass:
    alive = False
    def __init__(self) -> None:
        pass
    @dec("alive")
    def ping(self):
        print("pong")
        
        
class Vals(object):
    def __init__(self, vals:dict):
        self.__name__ = "Vals"
        self.vals = vals
    def to_dict(self):
        return self.serialize(data=self.vals, name=self.__name__)
    def serialize(self, **data: dict) -> dict:
        for key, value in data.items():
            if type(value) is dict:
                data[key] = self.serialize(**value)
            elif hasattr(value, "to_dict"):
                data[key] = self.serialize(**value.to_dict())

        return data
d = Vals({"sdsds":"sdfsdfsd", "sd":Vals({"sdfsdf":"sdfsdf"})})

print(d.to_dict())