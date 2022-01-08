import dataclasses

from flask import Flask, jsonify
from flask import request
from mysql.connector import connection

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
    description = request.json.get('description')
    if not description:
        return {}, 400
    try:
        item = ItemService().create(description)
        status_code = 201
    except ItemNotFoundException:
        return {}, 500
    return jsonify(dataclasses.asdict(item)), status_code


@app.route("/items", methods=['GET'])
def list_items():
    try:
        items = ItemService().list(amount=request.args.get('amount'),
                                    order_by=request.args.get('order_by'),
                                    order=request.args.get('order'))
        status_code = 200
    except Exception as e:
        print(e)
        items = []
        status_code = 404
    return jsonify([dataclasses.asdict(item) for item in items]), status_code


@app.route("/items/<item_id>", methods=['GET'])
def get_item(item_id):
    try:
        item_id = int(item_id)
        item = ItemService().find_by_id(item_id)
        status_code = 200
        pass
    except ItemNotFoundException:
        status_code = 404
        return jsonify({'error_code': 'ITEM_NOT_FOUND'}), status_code

    
    return jsonify(dataclasses.asdict(item)), status_code


@app.route("/items/<item_id>", methods=['PUT'])
def increment_item(item_id):
    increment = True if request.json.get('increment') else False
    if increment:
        try:
            item = ItemService().increment(item_id)
            status_code = 200
        except ItemNotFoundException:
            print(ItemNotFoundException)
            status_code = 404
            return jsonify({'error_code': 'ITEM_NOT_FOUND'}), status_code
        return jsonify(dataclasses.asdict(item)), status_code
    else:
        return {}, 200
