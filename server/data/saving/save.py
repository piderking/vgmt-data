from ..acceptor.table import TableResponse
import os
from ...env import CONFIG
from ...utils.log import info, warn
from datetime import datetime
import math
from ...utils.exceptions import FileWriteException
# temp config
UCOV = 60 # TODO MAKE this config arugments
SAVING_TIME_INTERVAL = 24 * UCOV # in amount of minutes
def save_table(table: TableResponse, uid: str, time: str | int, overwrite: bool = False) -> os.PathLike:
    # initalize table for save
    table.start_at_midnight()
    if CONFIG.data["local"] and CONFIG._valid_directory(CONFIG._replace(CONFIG.DATA["path"])): # check if local and create directory if it doens't exsist
        
        # str(CONFIG.DATA["file_structure"]).format(path_parameters["uid"], if type(path_parameters["day"]) is int else str(path_parameters["day"]) )
        if table.interval * len(table.data) > SAVING_TIME_INTERVAL:
            # Standard
            try:
                time =  datetime.strftime(int(time), CONFIG.DATA["time_pattern"]) # "%Y-%m-%dT%H:%M:%SZ"
            finally:
                ...
            


                
            file_path = CONFIG._replace(CONFIG.DATA["file_structure"]).format(uid, time)
            if os.path.exists(file_path):
                    if overwrite:
                        info("Overwriting file... options passed to save_table() function")
                    else:
                        warn("------------ THIS ACTION **WILL** OVERWRITE EXSISTING DATA ---------------")
                        if input("Continue? (y/n)").lower().strip().startswith("y"):
                            info("Overwriting...")
                        else: 
                            raise FileWriteException("Unable to overwrite exsisting file... User Cancelled Write Action")
                        
            CONFIG._valid_directory("/".join(file_path.split("/")[:-1]))

        #        data = csv.reader(string if not all(path_parameters.get("uid"), path_parameters.get("day")) else open(str(CONFIG.DATA["file_structure"]).format(path_parameters["uid"], datetime.strftime(int(path_parameters["day"], "%Y-%m-%dT%H:%M:%SZ")) if type(path_parameters["day"]) is int else str(path_parameters["day"]) )))
            f = open(file_path, "w");f.write(
                table.to_csv()
            );f.close()
            
        else:
            CONFIG._valid_directory("/".join(file_path.split("/")[:-1]))

            data = [table.data[t*SAVING_TIME_INTERVAL/UCOV:(t+1)*t*SAVING_TIME_INTERVAL/UCOV] for t in range(math.floor( table.interval * len(table.data) / SAVING_TIME_INTERVAL))]
            
            warn("------------ THIS ACTION MAY OVERWRITE EXSISTING DATA ---------------")
            info("Starting Saving Data Table with following arugments: \n\t Columns: {}, \t Starting Time: {}")
            for idx, frame in enumerate(data): 
            
            
                csv_string = CONFIG.DATA.get("csv_sep",",").join(table._cols + [table.time+(idx*SAVING_TIME_INTERVAL)])  + "\n"
            
                csv_string += "\n".join([",".join([str(col) for col in row]) for row in frame])
                
                try:
                    time =  datetime.strftime(int(time)*60, CONFIG.DATA["time_pattern"]) # "%Y-%m-%dT%H:%M:%SZ"
                finally:
                    ...
                    
                    
                file_path = CONFIG._replace(CONFIG.DATA["file_structure"]).format(uid, time)
                
                if os.path.exists(file_path):
                    if overwrite:
                        info("Overwriting file... options passed to save_table() function")
                    else:
                        warn("------------ THIS ACTION **WILL** OVERWRITE EXSISTING DATA ---------------")
                        if input("Continue? (y/n)").lower().strip().startswith("y"):
                            info("Overwriting...")
                        else: 
                            raise FileWriteException("Unable to overwrite exsisting file... User Cancelled Write Action")

                f = open(file_path, "w");f.write(
                    table.to_csv()
                );f.close()
                
                info("Saved {}/{}".format(idx), len(data))
            