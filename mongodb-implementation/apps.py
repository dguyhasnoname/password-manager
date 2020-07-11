import flask
from flask import request, jsonify, make_response, Response
from pymongo import MongoClient
import os, pyperclip, time, jsonschema, sys
from jsonschema import validate
from jsonschema import ValidationError
import simplejson as json
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
            errors = traceback.print_exc()
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
    accounts = dumps(tasks.find())
    return accounts

@app.route('/api/v1/accounts/id', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
def api_id_get():
    if flask.request.method == 'GET':
        id = action.get_id()
        if not id:
            return "\n[ERROR] Invalid request! Please provide an ID.\n"
        flag = ""
        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == id:
                pyperclip.copy(f.decrypt(account['password']).decode("utf-8"))
                return action.format_ouput(**account)
            else:
                flag = False
        if not flag:
            return "\n[WARNING] ID \"{}\" not found! Please provide correct ID.\n".format(id)

    elif flask.request.method == 'POST':
        json_data = request.get_json(force=True)
        errors = action.validate_json(json_data)
        if errors:
            return "\n[ERROR] Invalid JSON! \nValid JSON format:\n\n{}\n".format(action.schema['properties'])

        json_data['last_updated'] = datetime.utcnow()
        data = {"username": json_data['username'],
                "password": f.encrypt(json_data['password'].encode("utf-8")),
                "id": json_data['id'], 
                "url": json_data['url'],
                "last_updated": json_data['last_updated']
                }
        flag = ""
        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == json_data['id']:
                return "\n[WARNING] ID \"{}\" already exists!".format(account['id'])
            else:
                flag = True
        if flag: 
            tasks.insert_one(data).inserted_id
            return "\n[SUCCESS] ID \"{}\" saved!\n".format(json_data['id'])

    elif flask.request.method == 'DELETE':
        id = action.get_id()

        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == id:
                tasks.delete_one(account)
                return "\n[SUCCESS] ID \"{}\" deleted!\n".format(account['id'])   
            else:
                flag = True
        if flag: 
            return "\n[WARNING] ID \"{}\" not found!\n".format(id)  
    else:
        id = action.get_id()
        json_data = request.get_json(force=True)
        errors = action.validate_json(json_data)
        if errors:
            return "\n[ERROR] Invalid JSON! \nValid JSON format:\n\n{}\n".format(action.schema['properties'])
        json_data['last_updated'] = datetime.utcnow()
        data = {"username": json_data['username'],
                "password": f.encrypt(json_data['password'].encode("utf-8")),
                "id": json_data['id'], 
                "url": json_data['url'],
                "last_updated": json_data['last_updated']
                }        

        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == json_data['id']:
                tasks.replace_one(account, data, upsert=True)
                return "\n[SUCCESS] ID \"{}\" updated!".format(account['id'])   
            else:
                flag = True
        if flag: 
            return "\n[WARNING] ID \"{}\" not found!".format(id)         

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': 'This is the Home'})

if __name__ == '__main__':
    app.run(debug=True)