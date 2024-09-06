from .env import CONFIG
from .utils.actions import ActionLogger
actions: ActionLogger = ActionLogger.load(
    CONFIG.ACTIONS["file_path"]
)
