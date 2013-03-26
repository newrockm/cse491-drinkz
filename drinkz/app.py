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
        
    def ml_convert_form(self, environ, start_response):
        data = menu()
        data += ml_form()
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
        data += '<p><a href="/">Return to index</a></p>'
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
&nbsp;
[ <a href="inventory">Show Inventory</a> ]
&nbsp;
[ <a href="recipes">Show Recipes</a> ]
&nbsp;
[ <a href="convert">Convert to milliliters</a> ]
</p>
"""

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

