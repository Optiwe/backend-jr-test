import dataclasses

from flask import Flask, jsonify
from flask import request

from db import DB
from item import Item
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
    if not request.is_json:
        return jsonify({'error_code': 'BAD_REQUEST'}), 400
    try:
        description = request.json['description']
    except KeyError:
        return jsonify({'error_code': 'NO_DESCRIPTION_PROVIDED'}), 400

    item_service = ItemService()
    item = item_service.create(description)
    return jsonify(dataclasses.asdict(item)), 201


@app.route("/items", methods=['GET'])
def list_items():
    amount = request.args.get('amount')
    order_by = request.args.get('order_by')
    order = request.args.get('order')

    item_service = ItemService()
    try:
        items = item_service.list(
            amount=amount, order_by=order_by, order=order)
    except ValueError:
        return jsonify({'error_code': 'BAD_REQUEST'}), 400

    return jsonify([dataclasses.asdict(item) for item in items]), 200


@app.route("/items/<item_id>", methods=['GET'])
def get_item(item_id):
    item_service = ItemService()
    try:
        item_id = int(item_id)
        item = item_service.find_by_id(item_id)
    except ItemNotFoundException:
        return jsonify({'error_code': 'ITEM_NOT_FOUND'}), 404
    except ValueError:
        return jsonify({'error_code': 'CANNOT_PARSE_ITEM_ID'}), 400
    return jsonify(dataclasses.asdict(item)), 200


@app.route("/items/<item_id>", methods=['PUT'])
def increment_item(item_id):
    if not request.is_json:
        return jsonify({'error_code': 'BAD_REQUEST'}), 400

    item_service = ItemService()

    try:
        item_id = int(item_id)
        increment = request.json['increment']
    except ValueError:
        return jsonify({'err_code': 'CANNOT_PARSE_ITEM_ID'}), 400
    except KeyError:
        return jsonify({'err_code': 'BAD_REQUEST'}), 400

    if increment:
        item = item_service.increment(item_id)
        return jsonify(dataclasses.asdict(item)), 200
    else:
        return {}, 200
