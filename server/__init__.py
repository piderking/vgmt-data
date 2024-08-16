from flask import Flask, request, redirect, Response
from uuid import uuid4
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

@app.route("/endpoints/")
def all_endpoints():
    return {
        "clients": [{
            "name": client.name,
            "client_Id": "".join(["#" for _ in client.clientId[:len(client.clientId) - 5]]) + client.clientId[len(client.clientId) - 5:],
            "client_secret": "".join(["#" for _ in client.clientSecret[:len(client.clientSecret) - 5]]) + client.clientSecret[len(client.clientSecret) - 5:],
            "base_url": client.base_url,
            "redirect_url": client.redirect_url,
            "endpoints": client.endpoints,
            "state_users": client._state_users,
            "sandbox": client.sandbox,
            
            } for client in holder.clients],
        "amount": len(holder.clients)
    }
        
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
                return client._fetch_token(request.args.get("code"), request.args.get("state"), request.base_url, )
            else:
                return {
                    "status": "402",
                    "message": "Either state or code arguement is none, no bueno! Is None? -> State: {}, Code: {}".format(request.args.get("code") is None, request.args.get("state") is None)
                },  401
        # return request.args.get("code") + " | " + request.args.get("state")
    return {
            "status": "404",
            "message": "Requested enpoint ({}) is not found".format(endpoint)
        },  401

@app.route("/state_users/<endpoint>/users")
def endpoint_users(endpoint):
    logger.debug("{} Endpoint Used".format(endpoint))
    
    if endpoint is None or endpoint is "":
        return {
            "status": "401",
            "message": "Endpoint is None"
        },  401
    
    # All users of specific endpoint
    nlist = []
    for user in users:
        if user.get(endpoint) is not None:
            nlist.append(user) 
    return {
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
    }, 200
    

@app.route("/users/create/")
def create_user():
    return users.create_user(username=str(request.args.get("username") or ""), email=str(request.args.get("email") or ""),)

@app.route("/users/<uid>/delete/", methods=["POST, DELETE"])
def delete_user(uid):
    return users._remove_user(uid)

@app.route("/users/<uid>", methods=["GET"])
def view_user(uid):
    v = users.get(uid)
    return v if v is not None else {
        
    }
@app.route("/users/<uid>/claim/", methods=["GET"])
def transform(uid):
    endpoint = request.args.get("endpoint")
    state = request.args.get("state")
    
    if state is None or endpoint is None: 
        return {
            "message": "Endpoint: {} or State: {} not found".format(endpoint, state)
        }, 404

    for client in holder.clients:
        if client.name == endpoint:
            if client._transform_user(state, uid) is not None:
                return redirect("/users/{}".format(uid))
    return {
        "message": "Try again, no state user was found for the given state and user".format(endpoint,),
        "try-again":"/users/{}/claim?state={}&endpoint={}".format(uid, state, endpoint),
        
    }, 404

@app.route("/users/")
def all_current_users():
    return users.to_dict() # Get All Users
    
@app.route("/save/")
def save():
    logger.info("/save called, saving process comencing...")
    users.save(request.args.get("filename"))
    # TODO Add ClientAPI Saving
    # holder.save(request.args.get('filename'))
    
    logger.info("Saving Finished. Okay to exit.\n CTRL+C")
    return redirect("/")