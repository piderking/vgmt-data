from ..acceptor.table import TableResponse
import os
from ...env import CONFIG
from datetime import datetime
def save_table(table: TableResponse, uid: str, time: str | int) -> os.PathLike:
    
    if CONFIG.data["local"]:
        # str(CONFIG.DATA["file_structure"]).format(path_parameters["uid"], if type(path_parameters["day"]) is int else str(path_parameters["day"]) )
        try:
            time =  datetime.strftime(int(time), "%Y-%m-%dT%H:%M:%SZ")
        finally:
            ...
        


            
        file_path = CONFIG._replace(CONFIG.DATA["file_structure"]).format(uid, time)
        
        CONFIG._valid_directory("/".join(file_path.split("/")[:-1]))

    #        data = csv.reader(string if not all(path_parameters.get("uid"), path_parameters.get("day")) else open(str(CONFIG.DATA["file_structure"]).format(path_parameters["uid"], datetime.strftime(int(path_parameters["day"], "%Y-%m-%dT%H:%M:%SZ")) if type(path_parameters["day"]) is int else str(path_parameters["day"]) )))
        f = open(file_path, "w");f.write(
            table.to_csv()
        );f.close()