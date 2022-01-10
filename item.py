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

    def list(self, amount=None, order_by=None, order=None) -> List[Item]:
        """
        BE CAREFUL USING THIS METHOD, IT'S NOT SQL-INJECTION SAFE. IT SHOULD NOT RECIEVE USER INPUT
        :raise ValueError: If order is set and order_by is null.
        :raise ValueError: If order is other than 'DESC' or 'ASC'.
        :raise ValueError: If amount is not an int.
        """
        # I cannot use cursor.execute() in this method
        # since execute will escape order, making the query
        # look like: SELECT id FROM item ORDER BY 'id' DESC
        # This query will not output the desire results since id != 'id'
        # Therefore, I had to use python's string interpolation

        # TODO: better test this method?
        if order and not order_by:
            raise ValueError("order_by must be not null if order is not null")

        if not amount:
            amount = 10 ** 6
        amount = int(amount)

        if order.upper() not in ['ASC', 'DESC']:
            raise ValueError('order_by not valid')

        cursor = self.db.get_connection()

        query = f"""SELECT id, description, available_amount FROM {self.table_name}"""
        if order_by:
            query += f" ORDER BY {order_by}"
            if order:
                query += f" {order}"  # This line can cause SQL INJECTION
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
