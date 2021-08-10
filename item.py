import random
from dataclasses import dataclass
from typing import List, Optional
from multiprocessing import Lock
import time
import jsons
import  threading
from db import DB
lo = Lock() 
''' I added this global variable since increment test works with multiprocessing and every thread needs to know if the record is locked.
 There's probably a better solution to this, like modifying the test file and adding the lock there but I didn't want to change that file. '''

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
            sql = "INSERT INTO item (description, available_amount) VALUES (%s, %s)"
            val = (description, 0)
            cursor.execute(sql, val)
            item_id = cursor.lastrowid
        except Exception:
            print("Failed to create new item")
       
        return Item(item_id, description, 0)

    def list(self, amount=10, order_by='description', order='DESC') -> List[Item]:
        
        try:
            cursor = self.db.get_connection()
            sql = "SELECT * from item ORDER BY " + order_by + " " + order + " LIMIT " + str(amount)
            cursor.execute(sql)
            records = cursor.fetchall()

        except Exception:
            print("Failed to list items")
       
        items = jsons.load(records, List[Item])
        return items

    def find_by_id(self, item_id: int, lock=False) -> Optional[Item]:
        try:
            cursor = self.db.get_connection()
            sql = "SELECT * FROM item WHERE id = " + str(item_id)
            cursor.execute(sql)
            records = cursor.fetchone()
            if not records:
                return None
            item = jsons.load(records, Item)
            return item

        except Exception:
            print("Failed to find item")
      

    def increment(self, item: Item) -> Item:
        global lo
        with lo:
            try:
                cursor = self.db.get_connection()
                item_amount = self.find_by_id(item.id).available_amount
                amount = item_amount + 1
                sql = "UPDATE item SET available_amount = " + str(amount) + " WHERE id = " + str(item.id)
                cursor.execute(sql)
                updated_item = self.find_by_id(item.id)
                return updated_item

            except Exception:
                print("Failed to increment available amount of item: "+ str(item.description))
        