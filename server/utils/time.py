import time
from .int import isInt
import datetime

def convert_time(val: str | int) -> int:
    if isInt(val):
        return val
    else:
        # 2024-5-13T05:21:10
        return time.mktime(datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S").timetuple())


