from . import app, logger
from .env import DEBUG, HOST, PORT, TO_STDOUT
import os, sys


logger.info("Server Started")
app.run(
   debug=DEBUG,
   port=PORT,
   host=HOST,
)
logger.info("______________________________________")