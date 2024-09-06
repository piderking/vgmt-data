def serialize(**data: dict) -> dict:
    for key, value in data.items():
        if type(value) is dict:
            data[key] = serialize(**value)
        if type(value) is list:
            data[key] = list(serialize(**{str(idx):x for idx, x in enumerate(value)}).values())
        elif hasattr(value, "to_dict"):
            data[key] = serialize(**value.to_dict())
        # default to nothing
    return data
