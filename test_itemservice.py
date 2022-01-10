import dataclasses
import multiprocessing
import random
import string
from unittest import TestCase

import pytest

from db import DB
from itemservice import ItemService, ItemNotFoundException


class ItemServiceTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.item_service = ItemService()

    @staticmethod
    def _generate_random_string(length=10, use_numbers=True, use_letters=True):
        chars = ''
        if use_numbers:
            chars = chars + string.digits
        if use_letters:
            chars = chars + string.ascii_uppercase
        return ''.join(random.choices(chars, k=length))

    def test_create_item(self):
        item_description = self._generate_random_string()
        item = self.item_service.create(item_description)
        self.assertEqual(0, item.available_amount)
        self.assertEqual(item_description, item.description)

    def test_fetch_item_by_id(self):
        item_description = self._generate_random_string()
        item = self.item_service.create(item_description)
        item_id = item.id

        item = self.item_service.find_by_id(item_id)
        self.assertEqual(item_description, item.description)
        self.assertEqual(item_id, item.id)
        self.assertEqual(0, item.available_amount)

    def test_fetch_not_existing_item(self):
        with pytest.raises(ItemNotFoundException):
            self.item_service.find_by_id(random.randint(0, 1000000000))

    def test_list_items(self):
        first_item_description = self._generate_random_string()
        self.item_service.create(first_item_description)

        second_item_description = self._generate_random_string()
        self.item_service.create(second_item_description)

        items = self.item_service.list(amount=2, order_by='id', order='DESC')
        items_dict = [dataclasses.asdict(item) for item in items]
        self.assertEqual([{
            'id': AlwaysTrue(),
            'description': second_item_description,
            'available_amount': 0
        }, {
            'id': AlwaysTrue(),
            'description': first_item_description,
            'available_amount': 0
        }], items_dict)

    def test_list_items_wrong_params(self):
        with pytest.raises(ValueError):
            self.item_service.list(amount=2, order='DESC')

        with pytest.raises(ValueError):
            self.item_service.list(amount='NoNumber')

        with pytest.raises(ValueError):
            self.item_service.list(
                amount=2, order_by='id', order='NoValidOrder')

        with pytest.raises(ValueError):
            self.item_service.list(
                amount=2, order_by='NoValidAttr', order='ASC')

    def test_increment_item_available_amount(self):
        item_description = self._generate_random_string()
        item = self.item_service.create(item_description)
        item_id = item.id

        updated_item = self.item_service.increment(item_id)
        self.assertEqual(1, updated_item.available_amount)

        updated_item = self.item_service.find_by_id(item_id)
        self.assertEqual(1, updated_item.available_amount)

        updated_item = self.item_service.increment(item_id)
        self.assertEqual(2, updated_item.available_amount)

        updated_item = self.item_service.find_by_id(item_id)
        self.assertEqual(2, updated_item.available_amount)

    def test_consistent_increment(self):
        item_description = self._generate_random_string()
        item = self.item_service.create(item_description)
        self.assertEqual(0, item.available_amount)

        updated_item = self.item_service.find_by_id(item.id)
        self.assertEqual(0, updated_item.available_amount)

        def run(item_id):
            DB().clean_connection()
            item_service = ItemService()
            item_service.increment(item_id)

        jobs = []
        jobs_amount = 10
        for i in range(jobs_amount):
            p = multiprocessing.Process(target=run, args=(item.id,))
            jobs.append(p)
            p.start()

        for job in jobs:
            job.join()

        DB().clean_connection()

        updated_item = self.item_service.find_by_id(item.id)
        self.assertEqual(jobs_amount, updated_item.available_amount)


class AlwaysTrue(object):
    def __eq__(self, other):
        return other is not None
