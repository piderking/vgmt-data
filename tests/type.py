class him():
    def __init__(self) -> None:
        print("him")
        
class zee():
    def __init__(self) -> None:
        print("zee")
    
    def say_helo(self) -> None:
        print("hello")
class sdsd(zee, him):
    def __init__(self) -> None:
        
        zee.say_helo(self)
        
        
        
        
        print("sdsd")
        
        
def test(arg, **kwargs):
    print(arg, kwargs)

test(arg=1 )