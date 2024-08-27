def serialize(self, **data: dict) -> dict:
    for key, value in data.items():
        if type(value) is dict:
            data[key] = serialize(**value)
        elif hasattr(value, "to_dict"):
            data[key] = serialize(**value.to_dict())
            # default to nothing
    return data

