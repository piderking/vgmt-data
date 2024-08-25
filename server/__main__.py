from . import app, logger, users
from .env import DEBUG, HOST, PORT, TO_STDOUT
import os, sys
from .utils.saving import Saveable


logger.info("Server Started")
if __name__ == "__main__":

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
      
