from __future__ import print_function
import sys
import os
from flask import Flask, redirect, url_for, request, render_template, json, jsonify, Response
from pymongo import MongoClient
from bson import json_util, ObjectId

app = Flask(__name__)

client = MongoClient(os.environ['MONGO_CONNECTION_URI'],27017)
db = client.tododb

@app.route('/')
def todo():

    #_items = db.tododb.find()
    #items = [item for item in _items]
    #return render_template('todo.html', items=items)
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
    print('Delete Task JSON: ' + json_data[0], file=sys.stdout)
    oid = json_data[0]['oid']
    print('OID='+oid)

    if oid:
        entry = db.tododb.find_one({"_id": ObjectId(oid)})
        db.entry.remove(entry)

    return Response(json_util.dumps({"_id": ObjectId(oid)}), 200, {'ContentType':'application/json'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
