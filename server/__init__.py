from flask import Flask, request, redirect, Response
from uuid import uuid4

from .utils.time import convert_time

from .data.acceptor.table import TableResponse
from .env import *
import logging, colorlog
import sys
from .response import VSuccessResponse, VErrorResponse
from .utils.saving import Saveable
from .worker.endpoint import Endpoint, EndpointManager, users
from .data.web import DataResponse, DataRequest
from .utils.serialize import serialize
from .data.web import DataRequest, DataResponse, WebRequest, WebResponse
from .vars import actions
from .data.acceptor import cleaner, sorter, DataAcceptorCleaner, DataAcceptorSorter


app = Flask(__name__)
holder = EndpointManager()


table = TableResponse


@app.route("/")
def index():
    return redirect("/docs")

@app.route("/docs")
def docs():
    return VErrorResponse({}, 200, message="Unimplemented")

@app.route("/test")
def test():
    d = DataRequest.from_endpoint(holder.dexcom, path="get")._request(request={}, response={})
    print(d)
    return "OK"

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

@app.route("/users/<uid>/", methods=["GET"])
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
    
@app.route("/users/<uid>/refresh/<state>/", methods=["GET"])
def refresh_users_tokens(uid, state):
    uid = request.args.get("uid")
    state = request.args.get("state")
    
    if state is None or uid is None: 
        return VErrorResponse({
            "message": "Endpoint: {} or State: {} not found".format(uid, state)
        }, 404)

    client:Endpoint =  holder.__getattr__(uid)

    if client._refresh_token(users.get()) is not None:
        return redirect("/users/{}".format(uid)) # TODO Add redirect URL
    return VErrorResponse({
        "message": "Try again, no state user was found for the given state and user".format(uid,),
        "try-again":"/users/{}/claim?state={}&endpoint={}".format(uid, state, uid),
        
    }, 404)
    
@app.route("/users/<uid>/data/<endpoint>/", methods=["GET"])
def request_user_data(uid: str, endpoint: str):
    """Test Request for Dexcom
    
    """
    
    if uid is None or endpoint is None: 
        return VErrorResponse({
            "message": "Endpoint: {} or State: {} not found".format(uid, state)
        }, 404)

    client:Endpoint =  holder.__getattr__(endpoint)
    

    #if client._verify_token(users.get(uid)) is None:
    if users.get(uid, endpoint) is not None:
        data = DataRequest(**{
            "uid": uid,
            "time": 000000,
            "endpoint": endpoint,
            "path": "get",
            "access_token": users.get(uid, endpoint).access_token,
        })._request(
        **{
            "request": {
                "input": {       
                    "start" : {
                        "year": "2023",
                        "month": "12",
                        "day": "24",
                        "hour": "04",
                        "minute": "01",
                        "second": "50"
                    },
                    "end" : {
                        "year": "2023",
                        "month": "12",
                        "day": "24",
                        "hour": "05",
                        "minute": "01",
                        "second": "50"
                    }
                }
            },
            "response": {}
        }
        )
        
        DataResponse
        return VSuccessResponse({
            # fetch data here and return it
            "sucess": True,
            "data": data.to_dict()
        }, 200)
    return VErrorResponse({
        "message": "Try again, no state user was found for the given state and user".format(uid,),
        "try-again":"/users/{}/claim?state={}&endpoint={}".format(uid, "STATE", uid),
        
    }, 404)

@app.route("/users/<uid>/data/<endpoint>/", methods=["POST"])
def request_user_specific_data(uid: str, endpoint: str):
    """Sample Params

    Args:
        uid (str): _description_
        endpoint (str): endpoint of data
        
    {
        input: {
            structures of param field in "endpoints" defintion ({:[key].[field].[sub-field]})
        }
        time: Start time in secs from epoch from start time of data or 
        path: Config to Use
        
        
    }
    
    """
    req = request.json 
    
    if (uid is None or endpoint is None ) or not type(req) is dict: 
        return VErrorResponse({
            "message": "Incorrect Request Parameters: [uid:{}, endpoint:{}, request:{}]".format(uid, endpoint, str(req))
        }, 404)

    client:Endpoint =  holder.__getattr__(endpoint)
    
    
    if req.get("time") is None:
        return VErrorResponse({
        "message": "Try again, no start time user was found for the given params: {}".format(uid, str(req)),
        
        }, 404)
    #if client._verify_token(users.get(uid)) is None:
    if users.get(uid, endpoint) is not None:
        data = DataRequest(**{
            "uid": uid,
            "time": convert_time(req.get("time")),
            "endpoint": endpoint,
            "path": req.get("path", "get"),
            "access_token": users.get(uid, endpoint).access_token,
        })._request(
        **{
            "request": {
                "input": req.get("input"),
            },
            "response": req.get("response", {})
        }
        )
        
        DataResponse
        return VSuccessResponse({
            # fetch data here and return it
            "sucess": True,
            "data": data.to_dict()
        }, 200)
    return VErrorResponse({
        "message": "Try again, no state user was found for the given state and user".format(uid,),
        "try-again":"/users/{}/claim?state={}&endpoint={}".format(uid, "STATE", uid),
        
    }, 404)
@app.route("/users/")
def all_current_users():
    return users.to_dict() # Get All Users
    
    
@app.route("/save/")
def save():
    logger.info("/save called, saving process comencing...")

    users.save() # TODO Fix 
    actions.save()
    # Explicit Calls must be called to `Saveable`
    # holder.save(request.args.get('filename'))
    
    logger.info("Saving Finished. Okay to exit.\n CTRL+C")
    return redirect("/")

@app.route("/actions/")
def display_actions():
    return [serialize(**act.to_display()) for act in actions.actions]

