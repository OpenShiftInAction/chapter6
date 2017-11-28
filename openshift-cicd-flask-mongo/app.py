from __future__ import print_function
import sys
import os
import logging
from io import open
from flask import Flask, redirect, url_for, request, render_template, json, jsonify, Response
from pymongo import MongoClient
from bson import json_util, ObjectId
import configparser

app = Flask(__name__)

mongoclient_uri_str = ""

if os.path.isfile('/opt/app-root/mongo/mongodb_user') and os.path.isfile('/opt/app-root/mongo/mongodb_password') and os.path.isfile('/opt/app-root/mongo/mongodb_hostname') and os.path.isfile('/opt/app-root/mongo/mongodb_database'):
    mongodb_user = open('/opt/app-root/mongo/mongodb_user').readline().rstrip()
    mongodb_password = open('/opt/app-root/mongo/mongodb_password').readline().rstrip()
    mongodb_hostname = open('/opt/app-root/mongo/mongodb_hostname').readline().rstrip()
    mongodb_database = open('/opt/app-root/mongo/mongodb_database').readline().rstrip()
    print("Using files in /opt/app-root/mongo/ for MongoDB connection")
    mongoclient_uri_str = "mongodb://"+mongodb_user+":"+mongodb_password+"@"+mongodb_hostname+"/"+mongodb_database

elif os.environ.get('MONGO_CONNECTION_URI') is not None:
    print("Using environment variable MONGO_CONNECTION_URI for MongoDB connection")
    mongoclient_uri_str = os.environ['MONGO_CONNECTION_URI']

else:
    with open('/dev/termination-log', 'w') as file:
        file.write('This application requires a connection to a database, with credentials provided either:\n1. The following files available in /opt/app-root/mongo/: mongodb_user, mongodb_password, mongodb_hostname, mongodb_database\n2. Environment variable MONGO_CONNECTION_URI with the credentials to pass to the MongoClient library')
    exit()

try:
    client = MongoClient(mongoclient_uri_str, 27017)
    db = client.tododb
    print("Successful connection to MongoDB instance")
except:
    print("Error connecting to MongoDB with files")
    exit()

@app.route('/')
def todo():

    if os.path.isfile('/opt/app-root/ui/bgcolor.properties'):
        backgroundcolor = open('/opt/app-root/ui/bgcolor.properties').readline().rstrip()
        return render_template('todo.html', color=backgroundcolor)
    else:
        return render_template('todo.html')

@app.route('/gettasks')
def gettasks():

    json_docs = []
    _items = db.tododb.find()
    for item in _items:
        json_doc = json.dumps(item, default=json_util.default)
        json_docs.append(json_doc)

    return Response(json.dumps(json_docs), mimetype='application/json')

@app.route('/new', methods=['POST'])
def new():

    item_doc = {
        'name': request.form['name'],
        'description': request.form['completebydate']
    }
    db.tododb.insert_one(item_doc)

    return redirect(url_for('todo'))

@app.route('/addtask', methods=['POST'])
def addtask():

    json_data = request.get_json(force=True)
    _id = db.tododb.insert(json_data)
    return Response(json_util.dumps(_id), 200, {'ContentType':'application/json'})

@app.route('/deletetask', methods=['DELETE'])
def deletetask():

    json_data = request.get_json(force=True)
    print(json_data)
    oid = json_data[0].get('oid')
    print('OID='+oid)

    if oid:
        db.tododb.remove({"_id": ObjectId(oid)})

    return Response(json_util.dumps({"_id": ObjectId(oid)}), 200, {'ContentType':'application/json'})

if __name__ == "__main__":
    #Setting use_reloader=False - https://stackoverflow.com/questions/25504149/why-does-running-the-flask-dev-server-run-itself-twice
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
