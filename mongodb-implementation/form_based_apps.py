import flask
from flask import request, jsonify, make_response, render_template, redirect,url_for
from pymongo import MongoClient
import os, pyperclip, time, jsonschema
from jsonschema import validate, ValidationError
import simplejson as json
from bson import json_util
from bson.json_util import dumps, loads
from cryptography.fernet import Fernet
from datetime import datetime   
import traceback
import config as CONFIG
    
app = flask.Flask(__name__)

f = Fernet('%s' %(CONFIG.Config.PASSWORD_MANAGER_KEY)) # reads key from env via config.py
db = MongoClient('mongodb://%s:%s@127.0.0.1/accounts' % (CONFIG.Config.MONGO_USER, CONFIG.Config.MONGO_PASSWORD)) # connects to db by reading user/pwd from env via config.py
tasks = db.accounts.task  # Select the db collection name

class action:
    schema = {
        "type" : "object",
        "properties" : {
            "id" : {"type" : "string", "minLength": 3, "maxLength": 20},
            "username" : {"type" : "string", "minLength": 3, "maxLength": 20},
            "password" : {"type" : "string", "minLength": 5, "maxLength": 25},
            "url" : {"type" : "string"},
            "last_updated" : {"type" : "string"},
        },
        "additionalProperties": False, #prevents extra keys getting pushed
        "maxProperties": 5 
    }

    def validate_json(json_data):
        try:
            errors = jsonschema.validate(json_data, action.schema)
        except ValidationError as e:
            return [e.message]
        except Exception as e:
            traceback.print_exc()
            return e

    def get_id():
        try:
            id = request.args.get('id', type=str)
            return id
        except:
            return traceback.print_exc()

    def format_ouput(status=200, indent=4, sort_keys=True, **kwargs):
        response = make_response(dumps(dict(**kwargs), indent=indent, sort_keys=sort_keys))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['mimetype'] = 'application/json'
        response.status_code = status
        return response

@app.route('/api/v1/accounts/all', methods=['GET'])
def api_all():
    #return dumps(tasks.find())
    accounts = []
    for account in tasks.find():
        accounts.append({"id": account['id'], "username": account['username'], "url": account['url']})
    return jsonify(accounts)

@app.route('/')
def get_template():
    accounts = []
    for account in tasks.find():
        account['password'] = f.decrypt(account['password']).decode("utf-8")  
        accounts.append(account)
    return render_template("index.html",accounts=accounts)

@app.route('/api/v1/accounts/id', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
def api_id_get():
    if flask.request.method == 'GET':
        id = action.get_id()

        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == id:
                #account['password'] = f.decrypt(account['password']).decode("utf-8")
                return action.format_ouput(**account) 
            else:
                flag = False
        if not flag:
            return not_found(id)              

    elif flask.request.method == 'POST':
        errors = action.validate_json({"id": request.values.get("id"), 
                                        "username": request.values.get("username"),
                                        "password": request.values.get("password"),
                                        "url": request.values.get("url"),
                                        "last_updated": request.values.get("url")
                                        })
        if errors:
            return jsonify({"message": "Invalid JSON.", "valid_json": action.schema['properties']})
        data = {"id": request.values.get("id"), 
                "username": request.values.get("username"),
                "password": f.encrypt(request.values.get("password").encode("utf-8")),
                "url": request.values.get("url"),
                "last_updated": datetime.utcnow()
                }
        flag = ""
        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == data['id']:
                return jsonify({"id": data['id'], "message": "ID already exists. Try updating it."})
            else:
                flag = True
        if flag: 
            tasks.insert_one(data).inserted_id
            return redirect(url_for('get_template'))     
    else:
        return "[ERROR] Invalid request!"
      
@app.route('/api/v1/accounts/delete', methods=['GET'])
def api_id_delete():
    id = action.get_id()

    for account in tasks.find():
        account['id'] = str(account['id'])
        if account['id'] == id:
            tasks.delete_one(account)
            return redirect(url_for('get_template'))   
        else:
            flag = True
    if flag: 
        return not_found(id)

@app.route('/api/v1/accounts/update', methods=['POST'])
def api_id_update():
    errors = action.validate_json({"id": request.values.get("id"),
                                    "username": request.values.get("username"),
                                    "password": request.values.get("password"),
                                    "url": request.values.get("url"),
                                    "last_updated": request.values.get("url")
                                    })
    if errors:
        return jsonify({"message": "Invalid JSON.", "valid_json": action.schema['properties']})            
    data = {"id": request.values.get("id"), 
            "username": request.values.get("username"),
            "password": f.encrypt(request.values.get("password").encode("utf-8")),
            "url": request.values.get("url"),
            "last_updated": datetime.utcnow()
            }       

    for account in tasks.find():
        account['id'] = str(account['id'])
        if account['id'] == data['id']:
            tasks.replace_one(account, data, upsert=True)
            return redirect(url_for('get_template'))   
        else:
            flag = True
    if flag: 
        return not_found(data['id'])     

@app.route('/api/v1/accounts/pass', methods=['GET'])
def api_get_pass():
    id = action.get_id()

    for account in tasks.find():
        account['id'] = str(account['id'])
        if account['id'] == id:
            password = f.decrypt(account['password']).decode("utf-8")
            return jsonify({"account": id, "password": password})
        else:
            flag = False
    if not flag:
        return not_found(id)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'msg': 'This is a Test'})

@app.errorhandler(404)
def not_found(id):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
        'id' : id,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp 

if __name__ == '__main__':
    app.run(debug=True)