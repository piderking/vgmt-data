from flask import Flask, request, redirect
import logging, colorlog
import sys
from .env import *
import requests


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

@app.route("/valid")
def valid_endpoints():
    pass
        
@app.route("/endpoints/dexcom")
def dexcom():
    if request.args.get("code") is not None and request.args.get("state") is not None:
        logger.info("Auth Token: {}".format(str(request.args.get("code"))))
        holder[request.args.get("state")] = request.args.get("code")

        url = "https://sandbox-api.dexcom.com/v2/oauth2/token"

        payload = {
        "grant_type": "authorization_code",
        "code": "533d33c28705a6c8f06c2a3fde87da30",
        "redirect_uri": "http://172.28.244.153:3321/dexcom",
        "client_id": "buW1km1Ig6BfWwh0S0S5phKWhmQSse8t",
        "client_secret": "NVFP7f9QiBkFKriT"
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=payload, headers=headers)

        data = response.json()
        print(data)
        # return request.args.get("code") + " | " + request.args.get("state")
        return "Valid"
    else:
        return "Invalid"
