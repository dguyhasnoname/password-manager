import os, pyperclip
import simplejson as json
import flask
from flask import request, jsonify
from cryptography.fernet import Fernet
from getpass import getpass

#https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
app = flask.Flask(__name__)
app.config["DEBUG"] = True

global f
PASSWORD_MANAGER_KEY = os.getenv('PASSWORD_MANAGER_KEY', '/Users/mukund/.ssh/fernet_key')
with open(PASSWORD_MANAGER_KEY, "rb") as file:
    key = file.read()
    f = Fernet(key)

def write_json(data, filename='./static/data.json'):
    with open(filename,'w') as json_data: 
        json.dump(data, json_data, indent=4)
    return data

def render_data():
    filename = os.path.join(app.static_folder, './data.json')
    global accounts
    with open(filename) as json_file:
        accounts = json.load(json_file)
    return accounts   

# Home page msg
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Password-manager</h1>
<p>A prototype API for password management.</p>'''

# A route to return all of the available entries.
@app.route('/api/v1/accounts/all', methods=['GET'])
def api_all():
    render_data()
    return jsonify(accounts)

# A route to read/append/delete data.
@app.route('/api/v1/accounts/id', methods=['GET', 'POST', 'DELETE'])
def api_id_get():
    render_data()
    if flask.request.method == 'GET':
        if 'id' in request.args:
            id = str(request.args['id'])
        else:
            return "[ERROR]: No ID field provided. Please specify an ID."

        results = []

        for account in accounts:
            if account['id'] == id:
                results.append(account)
                pyperclip.copy(f.decrypt(account['password'].encode("utf-8")).decode("utf-8"))

        return jsonify(results)

    elif flask.request.method == 'POST':
        json_data = request.get_json(force=True)

        for account in accounts:
            if account['id'] == json_data['id']:
                return "[WARNING]: ID \"{}\" already exists!".format(json_data['id'])

        data = {"username": json_data['username'],
                "password": f.encrypt(json_data['password'].encode("utf-8")),
                "id": json_data['id'], 
                "url": json_data['url']
                }

        accounts.append(data) 
        write_json(accounts)
        return jsonify(data)

    else:
        if 'id' in request.args:
            id = str(request.args['id'])
        else:
            return "Error: No ID field provided. Please specify an ID."
        
        results = []

        for i in accounts:
            if i['id'] == id:
                data = [i for i in accounts if i['id'] != id]
                results = write_json(data)
        return jsonify(results)

# A route to read username data.
@app.route('/api/v1/accounts/username', methods=['GET'])
def api_username():
    render_data()
    if 'username' in request.args:
        username = str(request.args['username'])
    else:
        return "Error: No username field provided. Please specify an username."

    results = []

    for account in accounts:
        if account['username'] == username:
            results.append(account)
            pyperclip.copy(f.decrypt(account['password'].encode("utf-8")).decode("utf-8"))

    return jsonify(results)

app.run()