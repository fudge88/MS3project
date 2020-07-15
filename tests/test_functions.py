import os
import unittest

from app import app

from mockupdb import MockupDB, go, Command
from pymongo import MongoClient
from mockupdb._bson import ObjectId as mockup_oid
from json import dump


class DBSource(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.server = MockupDB(auto_ismaster=True, verbose=True)
        self.server.run()
        # create mongo connection to mock server

        app.testing = True
        app.config['MONGO_URI'] = self.server.uri
        self.app = app.test_client()

    @classmethod
    def tearDown(self):
        self.server.stop()


class TestUser(unittest.TestCase):

    ef test_addDataSource(self):
        # arrange
        id = '5a924d7a29a6e5484dcf68be'
        headers = [('Content-Type', 'application/json')]
        #   need to pass _id because pymongo creates one so it's impossible to match insert request without _ids
        toInsert = {'name': 'new', 'url': 'http://google.com',
                    '_id': id}
        future = go(self.app.put, '/dataSource',
                    data=dumps(toInsert), headers=headers)
        request = self.server.receives(
            Command({'insert': 'dataSources', 'ordered': True, 'documents': [{'name': 'new', 'url': 'http://google.com',
                                                                              '_id': mockup_oid(id)}]}, namespace='app'))
        request.ok(cursor={'inserted_id': id})

        # act
        http_response = future()

        # assert
        data = http_response.get_data(as_text=True)
        self.assertIn(id, data)
        self.assertEqual(http_response.status_code, 201)