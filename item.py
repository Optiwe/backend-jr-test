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
        try:
            cursor = self.db.get_connection()
            sql = f'INSERT INTO {self.table_name} (description, available_amount) VALUES (%s, %s)'
            cursor.execute(sql, (description, 0))
            self.db.commit()
            item_id = cursor.lastrowid
            cursor.close()
        except Exception as e:
            print(e)
            return None

        return Item(item_id, description, 0)

    def list(self, amount=None, order_by=None, order=None) -> List[Item]:
        try:
            cursor = self.db.get_connection()
            sql = f'SELECT * FROM {self.table_name}'
            if order_by:
                sql += f' ORDER BY {order_by}'
            if order:
                sql += f' {order}'
            if amount:
                sql += f' LIMIT {amount}'
            sql += ';'
            cursor.execute(sql)
            items = jsons.load(cursor.fetchall(), List[Item])
            cursor.close()
        except Exception as e:
            print(e)
            return []
        return items

    def find_by_id(self, item_id: int, lock=False) -> Optional[Item]:
        try:
            sql = f'SELECT * FROM {self.table_name} WHERE id = %s'
            cursor = self.db.get_connection()
            cursor.execute(sql, (item_id,))
            records = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(e)
            return None
        if not records:
            return None
        item = jsons.load(records[0], Item)
        return item

    def increment(self, item: Item) -> Item:
        try:
            cursor = self.db.get_connection()
            sql = f'UPDATE {self.table_name} SET available_amount = available_amount + 1 WHERE id = %s'
            cursor.execute(sql, (item.id,))
            self.db.commit()
            item = self.find_by_id(item.id)
            cursor.close()
        except Exception as e:
            print(e)
            return None
        return item