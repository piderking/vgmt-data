from flask import Flask, request, redirect, Response

from .env import *
import logging, colorlog
import sys
from .worker import ClientAPI, users
app = Flask(__name__)
holder = ClientAPI.from_toml(app)

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
        
@app.route("/endpoints/<endpoint>")
def endpoints(endpoint):
    logger.debug("{} Endpoint Used".format(endpoint))
    
    if endpoint is None or endpoint is "":
        return Response({
            "status": "401",
            "message": "Endpoint is None"
        },  status=401)
    for client in holder.clients:
        if client.name == endpoint:
            if request.args.get("code") is not None and request.args.get("state") is not None:
                return client._post(request.args.get("code"), request.args.get("state"), request.base_url, )
            else:
                return Response({
                    "status": "402",
                    "message": "Either state or code arguement is none, no bueno! Is None? -> State: {}, Code: {}".format(request.args.get("code") is None, request.args.get("state") is None)
                },  status=401)
        # return request.args.get("code") + " | " + request.args.get("state")
    return Response({
            "status": "404",
            "message": "Requested enpoint ({}) is not found".format(endpoint)
        },  status=401)
@app.route("/endpoints/<endpoint>/users")
def endpoint_users(endpoint):
    logger.debug("{} Endpoint Used".format(endpoint))
    
    if endpoint is None or endpoint is "":
        return Response({
            "status": "401",
            "message": "Endpoint is None"
        },  status=401)
    for client in holder.clients:
        if client.name == endpoint:
            return client._users
        # return request.args.get("code") + " | " + request.args.get("state")
    return Response({
            "status": "404",
            "message": "Requested enpoint ({}) is not found".format(endpoint)
        },  status=401)
@app.route("/endpoints/<endpoint>/user/<state>")
def endpoint_get_user(endpoint, state):
    logger.debug("{} Endpoint Used".format(endpoint))
    
    if endpoint is None or endpoint is "":
        return {
            "status": "401",
            "message": "Endpoint is None"
        },  401
    for client in holder.clients:
        if client.name == endpoint:
            return client.get_user(state)
                
        # return request.args.get("code") + " | " + request.args.get("state")
    return {
            "status": "404",
            "message": "Requested enpoint ({}) is not found".format(endpoint)
        }, 401

@app.route("/users")
def all_current_users():
    by = request.args.get("by")
    
    if by == "endpoint":
        return {client.name: client._users for client in holder.clients}
    return users
    
@app.route("/save")
def save():
    default = "data.json"
    if request.args.get("filename") is not None:
        default = request.args.get("filename")
    