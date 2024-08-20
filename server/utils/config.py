import os

class ConfigMissing(KeyError):
    def __init__(self, key: str, *args: object) -> None:
        print("{} was not found".format(key))
        super().__init__(*args)
        
class Config():
    def __init__(self, *args, **kwargs) -> None:
        """Configuration Class, all needed values are properties

        Raises:
            InvalidKwargs: _description_
        """
        self.args = args
        self.kwargs = kwargs
    
        """
        for (key, value) in kwargs:
            self.configs.append(key)
            self.__setattr__(key, value)
        """
    
    
    def __getattr__(self, key: str | int) -> any:
        """Get Attributes

        Args:
            key (str | int): Str pulls from kwargs, Int pulls from positional in args

        Returns:
            str | list | int | None: _description_
        """
        try:
            if type(key) is str:
                return self.kwargs[key.lower()]
            else:
                return self.args[int(key)]

        except KeyError as e:
            
            raise ConfigMissing(e)
        
        
    def _valid_directory(self, path: str) -> str:
        """Generated the directory if it doesn't exsist

        Args:
            path (str): Path for file or directory

        Returns:
            str: Path for file or directory
        """
        dir_path = "/".join(path.split("/")[:-1]) if path.split("/")[-1].find(".") else path
        print(dir_path, path)

        if not os.path.exists(dir_path):
            print("Directory: {} doesn't exsist")
            os.path.makedirs(dir_path)
        return path
    
    def _replace(self, path: str) -> str:
        path = path.split("/")
        for idx,val in enumerate(path):
            if val.find("<") != -1:
                for key in self.PATHS.keys():
                    if val == "<{}>".format(key):
                        path[idx] = self.PATHS[key]
        return self._valid_directory("/".join(path))
        """
                if len(path.split("<")) > -1:
            for folder in self.PATHS.keys():
                if folder in skip:
                    continue
                else:
                    return self._replace(  path.replace("<{}>".format( folder ), self.__getattr__(folder)), skip=skip + [folder] ) 
            return path
        else:
            print("sdfsdf")
            return self._valid_directory(path)
        """
          

