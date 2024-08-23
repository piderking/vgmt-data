from flask import Flask, request, redirect, Response
from uuid import uuid4
from .env import *
import logging, colorlog
import sys
from .response import VSuccessResponse, VErrorResponse
from .utils.saving import Saveable
from .worker.endpoint import EndpointManager, users
app = Flask(__name__)
holder = EndpointManager()

@app.route("/")
def index():
    return redirect("/docs")

@app.route("/docs")
def docs():
    return VErrorResponse({}, 200, message="Unimplemented")


@app.route("/endpoints/")
def all_endpoints():
    return VSuccessResponse({
        "clients": [client.to_dict() for client in holder.clients.values()],
        "amount": len(holder.clients.keys())

        
    }, code=200)

        
@app.route("/endpoints/<endpoint>")
def endpoints(endpoint):
    logger.debug("{} Endpoint Used".format(endpoint))
    
    if endpoint is None or endpoint == "":
        return VErrorResponse({
            "status": "401",
            "message": "Endpoint is None"
        },  401)
    client = holder.__getattr__(endpoint)
    print(client)
    if request.args.get("code") is not None and request.args.get("state") is not None:
        return VSuccessResponse(client._fetch_token(request.args.get("code"), request.args.get("state"), request.base_url, ), 200)
    else:
        return VErrorResponse({}, 401, message="Either state or code arguement is none, no bueno! Is None? -> State: {}, Code: {}".format(request.args.get("code") is None, request.args.get("state") is None))


@app.route("/endpoint/<endpoint>/tokens/")
def endpoint_users(endpoint):
    logger.debug("{} Endpoint Used".format(endpoint))
    
    if endpoint is None or endpoint == "":
        return VErrorResponse({}, 401, message="Requested enpoint ({}) is not found".format(endpoint)) 

    
    # All users of specific endpoint
    nlist = []
    for user in users:
        if user.get(endpoint) is not None:
            nlist.append(user) 
    return VSuccessResponse({
        "users": nlist,
        "count": len(nlist),
        "endpoint": endpoint,
        "args": [
            {
                "name": arg,
                "value": request.args.get(arg),
            }
            for arg in request.args.keys()
        ]
    }, 200)
    

@app.route("/users/create/")
def create_user():
    v =  users.create_user(username=str(request.args.get("username") or ""), email=str(request.args.get("email") or ""),)
    return VSuccessResponse(v, 200) if v is not None else VErrorResponse({}, 500, "Something happened... Not your fault")

@app.route("/users/<uid>/delete/", methods=["POST, DELETE"])
def delete_user(uid):
    v =  users._remove_user(uid)
    return VSuccessResponse(v, 200) if v is not None else VErrorResponse({}, 404, "No user found with UID of {}".format(uid))

@app.route("/users/<uid>", methods=["GET"])
def view_user(uid):
    v = users.get(uid)
    return VSuccessResponse(v, 200) if v is not None else VErrorResponse({}, 404, "User of UID::{} is None".format(uid))

@app.route("/users/<uid>/remove/", methods=["GET"]) # TODO Change to POST
def remove_user(uid):
    v = users._remove_user(uid)
    return VSuccessResponse(v, 200) if v is not None else VErrorResponse({}, 404, "User of UID::{} is None".format(uid))

@app.route("/users/<uid>/<provider>/remove/", methods=["GET"]) # TODO Change to POST
def remove_provider(uid, provider):
    v = users._remove_provider(uid, provider)
    return VSuccessResponse(v, 200) if v is not None else VErrorResponse({}, 404, "User of UID::{}::Provider::{} is None".format(uid, provider))


@app.route("/users/<uid>/claim/", methods=["GET"])
def transform(uid):
    endpoint = request.args.get("endpoint")
    state = request.args.get("state")
    
    if state is None or endpoint is None: 
        return VErrorResponse({
            "message": "Endpoint: {} or State: {} not found".format(endpoint, state)
        }, 404)

    client =  holder.__getattr__(endpoint)

    if client._transform_user(state, uid) is not None:
        return redirect("/users/{}".format(uid)) # TODO Add redirect URL
    return VErrorResponse({
        "message": "Try again, no state user was found for the given state and user".format(endpoint,),
        "try-again":"/users/{}/claim?state={}&endpoint={}".format(uid, state, endpoint),
        
    }, 404)

@app.route("/users/")
def all_current_users():
    return users.to_dict() # Get All Users
    
@app.route("/save/")
def save():
    logger.info("/save called, saving process comencing...")

    
    Saveable.save_all()
    # TODO Add ClientAPI Saving
    # holder.save(request.args.get('filename'))
    
    logger.info("Saving Finished. Okay to exit.\n CTRL+C")
    return redirect("/")