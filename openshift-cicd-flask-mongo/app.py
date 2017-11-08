import os

from flask import Flask, redirect, url_for, request, render_template, json, jsonify, Response
from pymongo import MongoClient
from bson import json_util, ObjectId

app = Flask(__name__)

client = MongoClient(os.environ['MONGO_CONNECTION_URI'],27017)
db = client.tododb

@app.route('/gettasks')
def gettasks():

    json_docs = []
    _items = db.tododb.find()
    for item in _items:
        json_doc = json.dumps(item, default=json_util.default)
        json_docs.append(json_doc)

    return Response(json.dumps(json_docs), mimetype='application/json')

@app.route('/addtask', methods=['POST'])
def addtask():

    json_data = request.get_json(force=True)
    _id = db.tododb.insert(json_data)
    return Response(json_util.dumps(_id), 200, {'ContentType':'application/json'})

@app.route('/deletetask', methods=['DELETE'])
def deletetask():

    json_data = request.get_json(force=True)
    oid = json_data[0]['oid']
    if oid:
        entry = db.tododb.find_one({"_id": ObjectId(oid)})
        db.entry.remove(entry)

    return Response(json_data, 200, {'ContentType':'application/json'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
