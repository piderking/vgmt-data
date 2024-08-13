from flask import Flask, request, redirect
import logging, colorlog
import sys

TO_STDOUT = True

handler = colorlog.StreamHandler()

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)


handler.setFormatter(colorlog.ColoredFormatter(
	'%(log_color)s%(levelname)s:%(name)s:%(message)s'))

if not TO_STDOUT: logging.basicConfig(filename='logs/server.log', level=logging.INFO)
else: logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = Flask(__name__)
holder = {}
@app.route("/")
def index():
    return redirect("/docs")

@app.route("/docs")
def docs():
    return {
        "status": "Invalid"
    }
@app.route("/state")
def state():
    state = request.args.get("state")
    if state is not None:
        if state in holder:
            return holder[state]
        
    return "Invalid"
        
@app.route("/dexcom")
def dexcom():
    if request.args.get("code") is not None and request.args.get("state") is not None:
        logger.info("Auth Token: {}".format(str(request.args.get("code"))))
        holder[request.args.get("state")] = request.args.get("code")
        return request.args.get("code") + " | " + request.args.get("state")
    else:
        return "Invalid"
