#!flask/bin/python
import flask
from flask import request, jsonify
from pymongo import MongoClient
import os, pyperclip
import simplejson as json
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

accounts = dumps(tasks.find())

@app.route('/api/v1/accounts/all', methods=['GET'])
def api_all():
    return accounts

@app.route('/api/v1/accounts/id', methods=['GET', 'POST', 'DELETE'])
def api_id_get():
    if flask.request.method == 'GET':
        if 'id' in request.args:
            id = str(request.args['id'])
        else:
            return "\n[ERROR]: No ID field provided. Please specify an ID."

        for account in tasks.find():
            account['id'] = str(account['id'])
           # account['password'] = str(account['password'])
            if account['id'] == id:
                pyperclip.copy(f.decrypt(account['password']).decode("utf-8"))
                account = str(account)
                return jsonify(account)

    elif flask.request.method == 'POST':
        json_data = request.get_json(force=True)

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
                return "\n[WARNING] ID \"{}\" already exists!".format(account['id'])
                sys.exit()
            else:
                flag = True
        if flag: 
            tasks.insert_one(data).inserted_id
            return "\n[SUCCESS] ID \"{}\" saved!".format(json_data['id'])

    else:
        if 'id' in request.args:
            id = str(request.args['id'])
        else:
            return "\n[ERROR]: No ID field provided. Please specify an ID."

        for account in tasks.find():
            account['id'] = str(account['id'])
            if account['id'] == id:
                tasks.delete_one(account)
                return "\n[OK] ID \"{}\" deleted!".format(account['id'])   
            else:
                flag = True
        if flag: 
            return "\n[WARNING] ID \"{}\" not found!".format(id)                     

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': 'This is the Home'})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'msg': 'This is a Test'})


if __name__ == '__main__':
    app.run(debug=True)