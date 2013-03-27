#! /usr/bin/env python

from wsgiref.simple_server import make_server
import urlparse
import db

dispatch = {
    '/' : 'index',
    '/bottletypes' : 'show_bottle_types',
    '/inventory' : 'show_inventory',
    '/recipes' : 'show_recipes',
    '/convert' : 'ml_convert_form',
    '/convertresult' : 'show_ml_convert',
}

html_headers = [('Content-type', 'text/html')]

class SimpleApp(object):
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
            
    def index(self, environ, start_response):
        data = menu()
        start_response('200 OK', list(html_headers))
        return [data]
        
    def show_bottle_types(self, environ, start_response):
        data = menu()
        data += """<table>
    <tr>
        <th>Manufacturer</th>
        <th>Liquor</th>
        <th>Type</th>
    </tr>
"""
        for (mfg, liquor, typ) in db.get_bottle_types():
            data += """
    <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
""" % (mfg, liquor, typ)
        data += "</table>"
        data += footer()
        start_response('200 OK', list(html_headers))
        return [data]

    def show_inventory(self, environ, start_response):
        data = menu()
        data += """<table>
    <tr>
        <th>Manufacturer</th>
        <th>Liquor</th>
        <th>Amount</th>
    </tr>
"""
        for (mfg, liquor) in db.get_liquor_inventory():
            amount = db.get_liquor_amount(mfg, liquor)
            data += """
    <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%f</td>
    </tr>
""" % (mfg, liquor, amount)
        data += "</table>"
        data += footer()
        start_response('200 OK', list(html_headers))
        return [data]

    def show_recipes(self, environ, start_response):
        data = menu()
        data += """<table>
    <tr>
        <th>Recipes</th>
        <th>Ingredients</th>
        <th>Missing Ingredients</th>
    </tr>
"""
        for recipe in db.get_all_recipes():
            ingredients = []
            for liquor, amount in recipe.ingredients:
                ingredients.append("%s %s" % (amount, liquor))
            ingredients = ', '.join(ingredients)

            missing_ingredients = []
            for liquor, amount in recipe.need_ingredients():
                missing_ingredients.append("%.2fml %s" % (amount, liquor))
            missing_ingredients = ', '.join(missing_ingredients)
            data += """
    <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
""" % (recipe.name, ingredients, missing_ingredients)
        data += "</table>"
        data += footer()
        start_response('200 OK', list(html_headers))
        return [data]

    def ml_convert_form(self, environ, start_response):
        data = menu()
        data += ml_form()
        data += footer()
        start_response('200 OK', list(html_headers))
        return [data]

    # http://webpython.codepoint.net/wsgi_request_parsing_post
    def show_ml_convert(self, environ, start_response):
        data = menu()

        if environ['REQUEST_METHOD'].endswith('POST'):
            body = None
            if environ.get('CONTENT_LENGTH'):
                length = int(environ['CONTENT_LENGTH'])
                body = environ['wsgi.input'].read(length)
                d = urlparse.parse_qs(body)
                try:
                    amount = "%s %s" % (d['amount'][0], d['unit'][0])
                    converted = db.convert_to_ml(amount)
                    data += "<p>%s is %d ml</p>" % (amount, converted)
                except KeyError:
                    data += "<p>Error processing form.</p>"
        data += footer()
        start_response('200 OK', list(html_headers))
        return [data]

    def error(self, environ, start_response):
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    
def menu():
    return """
<p>
View:
[ <a href="bottletypes">Show Bottle Types</a> ]
[ <a href="inventory">Show Inventory</a> ]
[ <a href="recipes">Show Recipes</a> ]
[ <a href="convert">Convert to milliliters</a> ]
</p>
"""

def footer():
    return '<p><a href="/">Return to index</a></p>'

def ml_form():
    return """
<form action="convertresult" method="post">
    Amount: <input type="text" name="amount" size="10">
    Unit: <select name="unit">
        <option value="ml">milliliters</option>
        <option value="l">liters</option>
        <option value="oz" selected="selected">ounces</option>
        <option value="gallon">gallons</option>
    </select>
    <input type="submit">
</form>
"""

