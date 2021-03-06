"""
Test WSGI app
"""

import unittest
import simplejson
import StringIO
from . import app, db, recipes

class TestWsgiApp(object):
    def setUp(self):
        self.status = None
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

        json_response = server(environ, self._start_response)
        response = simplejson.loads(json_response[0])

        return response

    def test_convert_units_to_ml(self):
        d = {
            'method':'convert_units_to_ml',
            'params':['5 oz'],
            'id':1
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

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
        assert self.status.startswith("200")

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
        assert self.status.startswith("200")

        assert response['error'] == None
        # tuples become lists
        assert response['result'] == [
            ['Gray Goose', 'vodka'],
            ['Johnnie Walker', 'black label'],
            ['Rossi', 'extra dry vermouth'],
            ["Uncle Herman's", 'moonshine']
        ]

    def test_add_bottle_type(self):
        self._initdb()
        d = {
            'method':'add_bottle_type',
            'params':['Captain Morgan', 'Dark Rum', 'spiced rum'],
            'id':4
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

        assert response['error'] == None
        assert response['result'] == 'OK'
        assert db._check_bottle_type_exists('Captain Morgan', 'Dark Rum')

    def test_add_inventory_1(self):
        # add with a bottle type that exists
        self._initdb()
        mfg = 'Johnnie Walker'
        liquor = 'black label'
        current_amount = db.get_liquor_amount(mfg, liquor)
        d = {
            'method':'add_inventory',
            'params':[mfg, liquor, '250 ml'],
            'id':5
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

        assert response['error'] == None
        assert response['result'] == 'OK'

        new_amount = db.get_liquor_amount(mfg, liquor)
        assert new_amount == current_amount + 250

    def test_add_inventory_2(self):
        # add with a bottle type that does not exist
        self._initdb()
        mfg = 'Ambrosia'
        liquor = 'nectar'
        d = {
            'method':'add_inventory',
            'params':[mfg, liquor, '250 ml'],
            'id':6
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

        assert response['error'] == None
        assert response['result'] != 'OK'

    def test_add_recipe_1(self):
        # add a recipe with 1 ingredient
        self._initdb()
        d = {
            'method':'add_recipe',
            'params':['scotch on the rocks', 'blended scotch', '4 oz'],
            'id':7
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

        assert response['error'] == None
        assert response['result'] == 'OK'

        r = db.get_recipe('scotch on the rocks')
        assert r != None

    def test_add_recipe_2(self):
        # add a recipe with two ingredients
        self._initdb()
        d = {
            'method':'add_recipe',
            'params':['vodka martini',
                'unflavored vodka', '6 oz',
                'vermouth', '1.5 oz'],
            'id':8
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

        assert response['error'] == None
        assert response['result'] == 'OK'

        r = db.get_recipe('vodka martini')
        assert r != None

    def test_add_recipe_3(self):
        # add a recipe with no ingredients
        self._initdb()
        d = {
            'method':'add_recipe',
            'params':'summer breeze',
            'id':9
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

        assert response['error'] == None
        assert response['result'] != 'OK'

        r = db.get_recipe('summer breeze')
        assert r == None

    def test_add_recipe_4(self):
        # add a recipe with a missing ingredient
        self._initdb()
        d = {
            'method':'add_recipe',
            'params':['vodka martini',
                'unflavored vodka', '6 oz',
                'vermouth'],
            'id':10
        }

        response = self._call_server(d)
        assert self.status.startswith("200")

        assert response['error'] == None
        assert response['result'] != 'OK'

        r = db.get_recipe('vodka martini')
        assert r == None

    def _start_response(self, status, response_headers, exc_info=None):
        self.status = status

