import flask
from flask import request, jsonify, make_response, render_template, redirect,url_for
from pymongo import MongoClient
import os, pyperclip, time, jsonschema
import simplejson as json
from bson.json_util import dumps, loads
from cryptography.fernet import Fernet
from datetime import datetime   
import config as CONFIG
    
app = flask.Flask(__name__)

f = Fernet('%s' %(CONFIG.Config.PASSWORD_MANAGER_KEY)) # reads key from env via config.py

db = MongoClient('mongodb://%s:%s@127.0.0.1/accounts' % (CONFIG.Config.MONGO_USER, CONFIG.Config.MONGO_PASSWORD)) # connects to db by reading user/pwd from env via config.py
tasks = db.accounts.task  # Select the db collection name

def format_ouput(status=200, indent=4, sort_keys=True, **kwargs):
    response = make_response(dumps(dict(**kwargs), indent=indent, sort_keys=sort_keys))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = status
    return response

def validate_json(data):
    schema = {
        "type" : "object",
        "properties" : {
            "id" : {"type" : "string", "minLength": 3, "maxLength": 20},
            "username" : {"type" : "string", "minLength": 3, "maxLength": 20},
            "password" : {"type" : "string", "minLength": 5, "maxLength": 25},
            "url" : {"type" : "string"},
            "last_updated" : {"type" : "string"},
        },
        "additionalProperties": False,
        "maxProperties": 5
    }
    if jsonschema.validate(data, schema):
        return True
    else:
        return "[ERROR] Invalid JSON!"  

def get_id():
    if 'id' in request.args:
        id = str(request.args['id'])
    else:
        return "\n[ERROR]: No ID field provided. Please specify an ID."
    return id

@app.route('/api/v1/accounts/all', methods=['GET'])
def api_all():
    accounts = dumps(tasks.find())
    return jsonify(accounts)

@app.route('/')
def get_template():
    accounts = tasks.find()
    return render_template("index.html",accounts=accounts)

@app.route('/api/v1/accounts/id', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
def api_id_get():
    if flask.request.method == 'GET':
        id = get_id()

        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == id:
                account['password'] = f.decrypt(account['password']).decode("utf-8")
                return format_ouput(**account)

    elif flask.request.method == 'POST':
        validate_json({"id": request.values.get("id"), 
                "username": request.values.get("username"),
                "password": request.values.get("password"),
                "url": request.values.get("url"),
                "last_updated": ""
                })
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
                return "\n[WARNING] ID \"{}\" already exists!".format(account['id'])
                sys.exit()
            else:
                flag = True
        if flag: 
            tasks.insert_one(data).inserted_id
            return redirect(url_for('get_template'))          
    else:
        return "[ERROR]"
      
@app.route('/api/v1/accounts/delete', methods=['GET'])
def api_id_delete():
    id = get_id()

    for account in tasks.find():
        account['id'] = str(account['id'])
        if account['id'] == id:
            tasks.delete_one(account)
            return redirect(url_for('get_template'))   
        else:
            flag = True
    if flag: 
        return "\n[WARNING] ID \"{}\" not found!".format(id) 

@app.route('/api/v1/accounts/update', methods=['POST'])
def api_id_update():
    validate_json({"id": request.values.get("id"),
            "username": request.values.get("username"),
            "password": request.values.get("password"),
            "url": request.values.get("url"),
            "last_updated": request.values.get("url")
            })
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
        return "\n[WARNING] ID \"{}\" not found! It can't be updated.".format(data['id'])        

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'msg': 'This is a Test'})

if __name__ == '__main__':
    app.run(debug=True)