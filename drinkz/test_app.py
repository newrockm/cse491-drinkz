"""
Test WSGI app
"""

import unittest
from . import app, db, recipes

class TestWsgiApp(object):
    def setUp(self):
        db._reset_db()

        db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
        db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')

        db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
        db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')
        
        db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
        db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

        db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
        db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')
        
    def test_wsgi_recipes(self):
        r = recipes.Recipe('whiskey lake', [('blended scotch', '6 liter')])
        db.add_recipe(r)

        server = app.SimpleApp()
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/recipes'
        }
        output = server.__call__(environ, fake_start_response)
        lookfor = """
    <tr>
        <td>whiskey lake</td>
        <td>6 liter blended scotch</td>
        <td>1000.00ml blended scotch</td>
    </tr>
"""

        assert lookfor in output[0]

def fake_start_response(status, response_headers, exc_info=None):
    # not actually going to do anything with the response
    pass
