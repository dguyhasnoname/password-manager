import flask
from flask import request, jsonify, make_response, render_template, redirect,url_for
from pymongo import MongoClient
import os, pyperclip, time
import simplejson as json
import jsonschema
from bson.json_util import dumps, loads
from cryptography.fernet import Fernet
from datetime import datetime   
    
app = flask.Flask(__name__)
app.config["DEBUG"] = True 
    
global f
PASSWORD_MANAGER_KEY = os.getenv('PASSWORD_MANAGER_KEY', '/Users/mukund/.ssh/fernet_key')
with open(PASSWORD_MANAGER_KEY, "rb") as file:
    key = file.read()
    f = Fernet(key)

client = MongoClient("mongodb://127.0.0.1:27017")  # host uri
db = client.accounts  # Select the database
tasks = db.task  # Select the collection name

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
            #account['password'] = str(account['password'])
            if account['id'] == id:
                account['password'] = f.decrypt(account['password']).decode("utf-8")
                #pyperclip.copy(f.decrypt(account['password'].encode("utf-8")).decode("utf-8"))
                return format_ouput(**account)

    elif flask.request.method == 'POST':
        validate_json({"username": request.values.get("username"),
                "password": request.values.get("password"),
                "id": request.values.get("id"), 
                "url": request.values.get("url"),
                "last_updated": ""
                })
        data = {"username": request.values.get("username"),
                "password": f.encrypt(request.values.get("password").encode("utf-8")),
                "id": request.values.get("id"), 
                "url": request.values.get("url"),
                "last_updated": datetime.utcnow()
                }
        

        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == data['id']:
                return "\n[WARNING] ID \"{}\" already exists!".format(account['id'])
                sys.exit()
            else:
                flag = True
        if flag: 
            tasks.insert_one(data).inserted_id
            #return "\n[SUCCESS] ID \"{}\" saved!".format(data['id'])
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
            #return "\n[SUCCESS] ID \"{}\" deleted!".format(id)
            return redirect(url_for('get_template'))   
        else:
            flag = True
    if flag: 
        return "\n[WARNING] ID \"{}\" not found!".format(id) 

@app.route('/api/v1/accounts/update', methods=['POST'])
def api_id_update():
    validate_json({"username": request.values.get("username"),
            "password": request.values.get("password"),
            "id": request.values.get("id"), 
            "url": request.values.get("url"),
            "last_updated": ""
            })
    data = {"username": request.values.get("username"),
            "password": f.encrypt(request.values.get("password").encode("utf-8")),
            "id": request.values.get("id"), 
            "url": request.values.get("url"),
            "last_updated": datetime.utcnow()
            }       

    for account in tasks.find():
        account['id'] = str(account['id'])
        if account['id'] == data['id']:
            tasks.replace_one(account, data, upsert=True)
            #return "\n[OK] ID \"{}\" updated!".format(account['id']) 
            return redirect(url_for('get_template'))   
        else:
            flag = True
    if flag: 
        return "\n[WARNING] ID \"{}\" not found!".format(id)        

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'msg': 'This is a Test'})

if __name__ == '__main__':
    app.run(debug=True)