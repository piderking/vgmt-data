from . import app, logger, users, holder
from .env import DEBUG, HOST, PORT, TO_STDOUT
import os, sys
from .utils.saving import Saveable
from .worker.user import needs_refresh # TODO Replace with refresh background task
from . import users, cleaner, sorter




logger.info("Server Started")
if __name__ == "__main__":

   sorter.start()
   
   for k in needs_refresh:
      # Get the endpoint amd then get the token 
      #print(users.get(k.get("uid"), k.get("endpoint")))
                       # default and set it
      print("Token Needs Refresh!", k)
      users + (k.get("uid"), k.get("endpoint"), holder.__getattr__(k.get("endpoint"))._refresh_token(users.get(k.get("uid"), k.get("endpoint"))))
      
   try:
      app.run(
         debug=DEBUG,
         port=PORT,
         host=HOST,
      )
      logger.info("______________________________________")
      
      logger.info("Server Ended >> Saving Commencing")
      # TODO Saving Here
      logger.info("Saving Complete! -> Exiting")
      
      
   except Exception as e:
      logger.error("{} has occurred", e)
   
   finally:
      sorter.join()
      cleaner.join()
      
