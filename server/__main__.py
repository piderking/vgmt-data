from . import app, logger
import os, sys



logger.info("Server Started")
app.run(
    debug=bool(os.environ.get("SERVER_DEBUG")) if os.environ.get("SERVER_DEBUG") else True,
    host=str(os.environ.get("SERVER_HOST")) if os.environ.get("SERVER_HOST") else "0.0.0.0",
    port=int(os.environ.get("SERVER_PORT")) if os.environ.get("SERVER_PORT") else 3321
)
logger.info("______________________________________")