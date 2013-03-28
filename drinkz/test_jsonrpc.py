"""
Test WSGI app
"""

import unittest
import simplejson
import StringIO
from . import app, db, recipes

class TestWsgiApp(object):
    def setUp(self):
        db._reset_db()

    def _initdb(self):
        db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
        db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

        db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
        db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')
        
        db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
        db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

        db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
        db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')
        
    def _init_recipes(self):
        r = recipes.Recipe('scotch on the rocks', [('blended scotch',
                                                   '4 oz')])
        db.add_recipe(r)

        r = recipes.Recipe('vodka martini', [('unflavored vodka', '6 oz'),
                                            ('vermouth', '1.5 oz')])
        db.add_recipe(r)

        r = recipes.Recipe('vomit inducing martini', [('orange juice',
                                                      '6 oz'),
                                                     ('vermouth',
                                                      '1.5 oz')])
        db.add_recipe(r)
 
        r = recipes.Recipe('whiskey bath', [('blended scotch', '2 liter')])
        db.add_recipe(r)

        r = recipes.Recipe('whiskey lake', [('blended scotch', '6 liter')])
        db.add_recipe(r)

    def _call_server(self, data):
        encoded = simplejson.dumps(data)
        inp = StringIO.StringIO(encoded)
        length = len(encoded)

        server = app.SimpleApp()
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/rpc',
            'CONTENT_LENGTH': length,
            'wsgi.input': inp
        }

        json_response = server.__call__(environ, fake_start_response)
        response = simplejson.loads(json_response[0])

        return response

    def test_convert_units_to_ml(self):
        d = {
            'method':'convert_units_to_ml',
            'params':['5 oz'],
            'id':1
        }

        response = self._call_server(d)

        assert response['error'] == None
        assert response['result'] == 147.87

    def test_get_recipe_names(self):
        self._initdb()
        self._init_recipes()
        d = {
            'method':'get_recipe_names',
            'params':[],
            'id':2
        }

        response = self._call_server(d)

        assert response['error'] == None
        assert response['result'] == [
            'scotch on the rocks',
            'vodka martini',
            'vomit inducing martini',
            'whiskey bath',
            'whiskey lake'
        ]

    def test_get_liquor_inventory(self):
        self._initdb()
        d = {
            'method':'get_liquor_inventory',
            'params':[],
            'id':3
        }

        response = self._call_server(d)

        assert response['error'] == None
        # tuples become lists
        assert response['result'] == [
            ['Gray Goose', 'vodka'],
            ['Johnnie Walker', 'black label'],
            ['Rossi', 'extra dry vermouth'],
            ["Uncle Herman's", 'moonshine']
        ]


def fake_start_response(status, response_headers, exc_info=None):
    # not actually going to do anything with the response
    pass

