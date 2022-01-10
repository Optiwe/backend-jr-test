import random
from dataclasses import dataclass
from typing import List, Optional

import jsons

from db import DB


@dataclass
class Item(object):
    id: int
    description: str
    available_amount: int


class ItemDAO(object):
    table_name = 'item'

    def __init__(self):
        self.db = DB()

    def create(self, description: str) -> Item:
        cursor = self.db.get_connection()

        query = f"""INSERT INTO {self.table_name} (description, available_amount)
					VALUES (%s, 0)"""
        data = (description,)

        cursor.execute(query, data)
        item_id = cursor.lastrowid
        self.db.commit()

        return Item(item_id, description, 0)

    @staticmethod
    def check_list_orders(order_by, order):
        if order and not order_by:
            raise ValueError("order_by must be not null if order is not null")

        if order.upper() not in ['ASC', 'DESC']:
            raise ValueError('order_by not valid')

        item_attrs = ['id', 'description', 'available_amount']
        order_by = order_by.split(',')
        for attr in order_by:
            if attr not in item_attrs:
                raise ValueError('order_by not valid')

    def list(self, amount=None, order_by=None, order=None) -> List[Item]:
        """
        :raise ValueError: If order_by is not an item valid attribute.
        :raise ValueError: If order is set and order_by is null.
        :raise ValueError: If order is other than 'DESC' or 'ASC'.
        :raise ValueError: If amount is not an int.
        """
        # I cannot use cursor.execute() in this method to sanite the input
        # since execute will escape order, making the query
        # look like: SELECT id FROM item ORDER BY 'id' DESC
        # This query will not output the desire results since id != 'id'
        # Therefore, I had to use python's string interpolation

        if not amount:
            amount = 10 ** 6
        amount = int(amount)
        self.check_list_orders(order_by, order)

        cursor = self.db.get_connection()

        query = f"""SELECT id, description, available_amount FROM {self.table_name}"""
        if order_by:
            query += f" ORDER BY {order_by}"
            if order:
                query += f" {order}"
        query += f" LIMIT {amount}"

        cursor.execute(query)
        records = cursor.fetchall()

        if not records:
            return []
        items = jsons.load(records, List[Item])
        return items

    def find_by_id(self, item_id: int, lock=False) -> Optional[Item]:
        """
        :param lock: Sets a share lock on item's table.
        """
        cursor = self.db.get_connection()

        if lock:
            cursor.execute(f"LOCK TABLES {self.table_name} READ")

        query = f""" SELECT id, description, available_amount FROM {self.table_name}
                     WHERE id = %s"""
        cursor.execute(query, (item_id,))
        records = cursor.fetchall()

        if lock:
            cursor.execute("UNLOCK TABLES")

        if not records:
            return None

        item = jsons.load(records[0], Item)
        return item

    def increment(self, item: Item) -> Item:
        query = f"""UPDATE {self.table_name}
 			        SET  available_amount = available_amount + 1
         			WHERE id = %s
         		"""
        data = (item.id, )

        cursor = self.db.get_connection()
        cursor.execute(query, data)

        item = self.find_by_id(item.id, lock=True)

        return item
