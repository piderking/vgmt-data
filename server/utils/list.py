from typing import Any


type AcceptableLabelName = str

def position_at(data: list[AcceptableLabelName], label: AcceptableLabelName) -> int | None:
    for idx, slabel in enumerate(data):
        if label == slabel:
            return idx
    
    return None

def transform(data: list[list[Any]]) -> list[list[Any]]:
    d = list(zip(*data))
    return [[p[y] for p in d] for y in range(len(d[0]))]
    

def gen[T: any](times: int, val: T = None) -> list[T]:
    """Generate Value n times

    Args:
        times (int): Times to generate value
        val (any, optional): Value in list. Defaults to None.

    Returns:
        int: 
    """
    return [val for _  in range(times)]
