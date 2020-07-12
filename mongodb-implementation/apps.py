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
        if jsonschema.validate(json_data, action.schema):
            return jsonify({"message": "Invalid JSON.", "valid_json": action.schema['properties']})
        # except ValidationError as e:
        #     errors = traceback.print_exc()
        #     return errors

    def get_id():
        id = request.args.get('id', type=str)
        return id

@app.route('/api/v1/accounts/all', methods=['GET'])
def api_all():
    accounts = dumps(tasks.find())
    return accounts

@app.route('/api/v1/accounts/id', methods=['GET', 'POST', 'DELETE', 'UPDATE'])
def api_id_get():
    if flask.request.method == 'GET':
        id = action.get_id()
        if id == "":
            return not_found(id)

        flag = ""
        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == id:
                pyperclip.copy(f.decrypt(account['password']).decode("utf-8"))
                return make_response(dumps(dict(account), indent=4, sort_keys=True))
            else:
                flag = False
        if not flag:
            return not_found(id)

    elif flask.request.method == 'POST':
        json_data = request.get_json(force=True)
        errors = action.validate_json(json_data)
        if errors:
            return jsonify({"message": "Invalid JSON.", "valid_json": action.schema['properties']})

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
                return jsonify({"id": json_data['id'], "message": "ID already exists. Try updating it."})
            else:
                flag = True
        if flag: 
            tasks.insert_one(data).inserted_id
            return jsonify({"message": "inserted", "status": 200, "inserted_data": str(data)})

    elif flask.request.method == 'DELETE':
        id = action.get_id()
        if id == "":
            return not_found(id)

        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == id:
                tasks.delete_one(account)
                return jsonify({"message": "deleted", "status": 200, "deleted_id": id})
            else:
                flag = True
        if flag:
            return not_found(id)
    else:
        json_data = request.get_json(force=True)
        errors = action.validate_json(json_data)
        # if errors:
        #     return jsonify({"message": "Invalid JSON.", "valid_json": action.schema['properties']})
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
                return jsonify({"message": "updated", "status": 200, "updated_json": data})
            else:
                flag = True
        if flag:
            return not_found(json_data['id'])

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': 'This is the Home'})

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