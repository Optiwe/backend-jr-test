import dataclasses
import json

from flask import Flask, jsonify, request

from db import DB
from itemservice import ItemService, ItemNotFoundException

app = Flask(__name__)


@app.route("/status", methods=['GET'])
def status():
    db = DB()
    connection = db.get_connection()
    connection.execute('SELECT 1 cache')
    results = connection.fetchall()
    if not results:
        return {}, 500

    result = results[0]
    if result.get('cache', 0) != 1:
        return {}, 500

    return {}, 200


@app.route("/items", methods=['POST'])
def create_item():
    itemservice = ItemService()
    description = json.loads(request.data)['description']
    if not description:
        return {}, 400

    item = itemservice.create(description)
    if not item:
        return {}, 500
    
    return jsonify(dataclasses.asdict(item)), 201
    

@app.route("/items", methods=['GET'])
def list_items():
    itemservice = ItemService()
    amount = request.args['amount']
    order_by = request.args['order_by']
    order = request.args['order']
    if not amount or not order_by or not order:
        return {}, 400

    items = itemservice.list(amount, order_by, order)
    if not items:
        return {}, 500

    return jsonify([dataclasses.asdict(item) for item in items]), 200


@app.route("/items/<item_id>", methods=['GET'])
def get_item(item_id):
    itemservice = ItemService()
    try:
        item = itemservice.find_by_id(item_id)  
        pass
    except ItemNotFoundException:
    
        return jsonify({'error_code': 'ITEM_NOT_FOUND'}), 404

    return jsonify(dataclasses.asdict(item)), 200


@app.route("/items/<item_id>", methods=['PUT'])
def increment_item(item_id):
    itemservice = ItemService()
    increment = json.loads(request.data)['increment']
    if increment:
        try:
            item = itemservice.increment(item_id)
        except ItemNotFoundException:
            
            return jsonify({'error_code': 'ITEM_NOT_FOUND'}), 404
        return jsonify(dataclasses.asdict(item)), 200
    else:
        return {}, 200
