config_path = "data/config"
def _replace(path: str):
    if len(path.split("<")):
        return path.replace("<{}>".format("config_path"), config_path)
    else:
        return path
    
print(_replace("<config_path>/hello.py"))