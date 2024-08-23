from . import app, logger
from .env import DEBUG, HOST, PORT, TO_STDOUT
import os, sys
from .utils.saving import to_save, Saveable


logger.info("Server Started")
try:
   app.run(
      debug=DEBUG,
      port=PORT,
      host=HOST,
   )
   logger.info("______________________________________")


except Exception as e:
   logger.error("{} has occurred", e)
   
   
logger.info("Server Ended >> Saving Commencing")
Saveable.save_all()
logger.info("Saving Complete! -> Exiting")