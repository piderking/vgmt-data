def _get(arg):
    def decorator(function):
        def wrapper(*args, **kwargs):
            print(arg)
            result = function(*args, **kwargs)
            return result
        return wrapper
    return decorator


class t:
    def __init__(self) -> None:
        self.hi = 0
        print("hi")
    @_get(d="sd")
    def run(self):
        print("dfgdfg")
        print(self.hi)
    
dt = t()
dt.run()