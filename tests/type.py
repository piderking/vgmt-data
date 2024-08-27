class Seriable():
    val = "Value"
    def __format__(self, format_spec: str) -> str:
        return self.__getattribute__(format_spec)
    
v = Seriable()
