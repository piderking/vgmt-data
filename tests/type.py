import json

actions = []


@log()    
def add(i: int, x: int | str, **kwargs: dict) -> int:
    return i+x


add(1, 2, hello=False)

print(actions)
print(actions[0].to_dict())

json.dumps(actions[0].to_dict())