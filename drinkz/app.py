#! /usr/bin/env python

from wsgiref.simple_server import make_server
import jinja2
import simplejson
import urlparse
import db

dispatch = {
    '/' : 'index',
    '/bottletypes' : 'show_bottle_types',
    '/add_bottletype': 'add_bottle_type',
    '/inventory' : 'show_inventory',
    '/recipes' : 'show_recipes',
    '/canmake' : 'show_can_make',
    '/convert' : 'ml_convert_form',
    '/convertresult' : 'show_ml_convert',
    '/rpc' : 'dispatch_rpc'
}

html_headers = [('Content-type', 'text/html')]

class SimpleApp(object):
    def __init__(self):
        loader = jinja2.FileSystemLoader('./drinkz/templates')
        self.jenv = jinja2.Environment(loader=loader)

    def __call__(self, environ, start_response):

        path = environ['PATH_INFO']
        fn_name = dispatch.get(path, 'error')

        # retrieve 'self.fn_name' where 'fn_name' is the
        # value in the 'dispatch' dictionary corresponding to
        # the 'path'.
        fn = getattr(self, fn_name, None)

        if fn is None:
            start_response("404 Not Found", html_headers)
            return ["No path %s found" % path]

        return fn(environ, start_response)
        
    def _render(self, filename, title, vars = {}):
        template = self.jenv.get_template(filename)
        vars['title'] = title
        return template.render(vars).__str__()

    def load_db(self, filename):
        db.load_db(filename)

    def index(self, environ, start_response):
        data = self._render('index.html', 'index')
        start_response('200 OK', list(html_headers))
        return [data]
        
    def show_bottle_types(self, environ, start_response):
        vars = {}
        if environ['REQUEST_METHOD'].endswith('POST'):
            vars['error'] = self.do_add_bottle_type(environ)

        vars['bottle_types'] = db.get_bottle_types()
        data = self._render('bottletypes.html', 'Show Bottle Types', vars)
        start_response('200 OK', list(html_headers))
        return [data]

    def add_bottle_type(self, environ, start_response):
        data = self._render('form_bottletype.html', 'Add Bottle Type')
        start_response('200 OK', list(html_headers))
        return [data]

    def do_add_bottle_type(self, environ):
        error = None
        if environ.get('CONTENT_LENGTH'):
            length = int(environ['CONTENT_LENGTH'])
            body = environ['wsgi.input'].read(length)
            d = urlparse.parse_qs(body)
            try:
                mfg = d['mfg'][0]
                liquor = d['liquor'][0]
                typ = d['typ'][0]
                db.add_bottle_type(mfg, liquor, typ)
            except (KeyError, ValueError):
                error = "Error processing form."

    def show_inventory(self, environ, start_response):
        inventory = []
        for (mfg, liquor) in db.get_liquor_inventory():
            amount = db.get_liquor_amount(mfg, liquor)
            inventory.append((mfg, liquor, amount))
        vars = {'inventory': inventory}
        data = self._render('inventory.html', 'Show Inventory', vars)
        start_response('200 OK', list(html_headers))
        return [data]

    def show_recipes(self, environ, start_response):
        recipes = []
        for rec in db.get_all_recipes():
            ingredients = []
            for liquor, amount in rec.ingredients:
                ingredients.append("%s %s" % (amount, liquor))
            ingredients = ', '.join(ingredients)

            missing_ingredients = []
            for liquor, amount in rec.need_ingredients():
                missing_ingredients.append("%.2fml %s" % (amount, liquor))
            missing_ingredients = ', '.join(missing_ingredients)

            recipes.append((rec.name, ingredients, missing_ingredients))
        vars = {'recipes': recipes}
        data = self._render('recipes.html', 'Show Recipes', vars)
        start_response('200 OK', list(html_headers))
        return [data]

    def show_can_make(self, environ, start_response):
        can_make = []
        for rec in db.get_all_recipes():
            missing = rec.need_ingredients()
            if len(missing) == 0:
                can_make.append(rec)

        recipes = []
        for rec in can_make:
            ingredients = []
            for liquor, amount in rec.ingredients:
                ingredients.append("%s %s" % (amount, liquor))
            ingredients = ', '.join(ingredients)
            recipes.append((rec.name, ingredients))

        vars = {'recipes': recipes}
        data = self._render('canmake.html', 'Recipes you can make', vars)
        start_response('200 OK', list(html_headers))
        return [data]

    def ml_convert_form(self, environ, start_response):
        data = self._render('convert.html', 'Convert to Milliliters')
        start_response('200 OK', list(html_headers))
        return [data]

    # http://webpython.codepoint.net/wsgi_request_parsing_post
    def show_ml_convert(self, environ, start_response):
        vars = {}

        if environ['REQUEST_METHOD'].endswith('POST'):
            body = None
            if environ.get('CONTENT_LENGTH'):
                length = int(environ['CONTENT_LENGTH'])
                body = environ['wsgi.input'].read(length)
                d = urlparse.parse_qs(body)
                try:
                    amount = "%s %s" % (d['amount'][0], d['unit'][0])
                    converted = db.convert_to_ml(amount)
                    vars['amount'] = amount
                    vars['converted'] = converted
                except (KeyError, ValueError):
                    vars['error'] = "Error processing form."

        data = self._render('convertresult.html', 'Convert to Milliliters Result', vars)
        start_response('200 OK', list(html_headers))
        return [data]

    def error(self, environ, start_response):
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response(status, list(html_headers))
        return [data]

    def dispatch_rpc(self, environ, start_response):
        # POST requests deliver input data via a file-like handle,
        # with the size of the data specified by CONTENT_LENGTH;
        # see the WSGI PEP.
        
        if environ['REQUEST_METHOD'].endswith('POST'):
            body = None
            if environ.get('CONTENT_LENGTH'):
                length = int(environ['CONTENT_LENGTH'])
                body = environ['wsgi.input'].read(length)
                response = self._dispatch(body) + '\n'
                start_response('200 OK', [('Content-Type', 'application/json')])

                return [response]

        # default to a non JSON-RPC error.
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response(status, list(html_headers))
        return [data]
    
    def _decode(self, json):
        return simplejson.loads(json)

    def _dispatch(self, json):
        rpc_request = self._decode(json)

        method = rpc_request['method']
        params = rpc_request['params']
        
        rpc_fn_name = 'rpc_' + method
        fn = getattr(self, rpc_fn_name)
        result = fn(*params)

        response = { 'result' : result, 'error' : None, 'id' : 1 }
        response = simplejson.dumps(response)
        return str(response)

    def rpc_convert_units_to_ml(self, amount):
        return round(db.convert_to_ml(amount), 2)

    def rpc_get_recipe_names(self):
        names = []
        for r in db.get_all_recipes():
            names.append(r.name)
        names.sort()
        return names

    def rpc_get_liquor_inventory(self):
        inventory = []
        for inv in db.get_liquor_inventory():
            inventory.append(inv)
        inventory.sort()
        return inventory

