def isInt(val: int or any) -> bool:
    try: 
        int(val)
        return True
    except ValueError:
        return False