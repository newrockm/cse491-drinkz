from drinkz import db
from drinkz import recipes
import os
import sys

if len(sys.argv) != 2:
    print >>sys.stderr, "Usage: %s <filename>" % sys.argv[0]
    sys.exit(1)

db.load_db(sys.argv[1])

# everything will go into the html directory
try:
    os.mkdir('html')
except OSError:
    # already exists
    pass

# nav bar
base_url = 'http://www.cse.msu.edu/~newrockm/cse491/drinkz'
index_link = '<a href="%s/index.html">Index</a>' % base_url
liquor_types_link = '<a href="%s/liquor_types.html">Liquor Types</a>' % base_url
inventory_link = '<a href="%s/inventory.html">Inventory</a>' % base_url
recipes_link = '<a href="%s/recipes.html">Recipes</a>' % base_url

navbar = """
<div style="text-align:center">
    [ %s 
    | %s 
    | %s 
    | %s ]
</div>""" % (index_link, liquor_types_link, inventory_link, recipes_link)

# header and footer

header = """<html>
<head>
<title>%s</title>
<style>
    table {border-collapse:collapse;}
    table,th, td {border: 1px solid black;}
</style>
</head>
<body>
"""

footer = """</body>
</html>
"""

# index.html

fp = open('html/index.html', 'w')
print >>fp, header % 'Index'
print >>fp, navbar
print >>fp, """
<h2>Index</h2>
<p>%s</p>
<p>%s</p>
<p>%s</p>
""" % (liquor_types_link, inventory_link, recipes_link)
print >>fp, footer
fp.close()

# liquor_types.html

fp = open('html/liquor_types.html', 'w')
print >>fp, header % 'Liquor Types'
print >>fp, navbar
print >>fp, """
<h2>Liquor Types</h2>
<table>
  <tr>
    <th>Manufacturer</th>
    <th>Liquor</th>
    <th>Type</th>
  </tr>
"""

for manufacturer, liquor, typ in db.get_bottle_types():
    print >>fp, """  <tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
  </tr>
""" % (manufacturer, liquor, typ)

print >>fp, "</table>"
print >>fp, footer
fp.close()

# inventory.html

fp = open('html/inventory.html', 'w')

print >>fp, header % 'Inventory'
print >>fp, navbar
print >>fp, """
<h2>Inventory</h2>
<table>
  <tr>
    <th>Manufacturer</th>
    <th>Liquor</th>
    <th>Amount</th>
  </tr>
"""

for manufacturer, liquor in db.get_liquor_inventory():
    amount = db.get_liquor_amount(manufacturer, liquor)
    print >>fp, """  <tr>
    <td>%s</td>
    <td>%s</td>
    <td style="text-align: right">%.2f ml</td>
  </tr>
""" % (manufacturer, liquor, amount)

print >>fp, "</table>"
print >>fp, footer
fp.close()

# recipes.html

fp = open('html/recipes.html', 'w')

print >>fp, header % 'Recipes'
print >>fp, navbar
print >>fp, """
<h2>Recipes</h2>
<table>
  <tr>
    <th>Recipe Name</th>
    <th>Have Ingredients</th>
  </tr>
"""

for recipe in db.get_all_recipes():
    if recipe.need_ingredients():
        have_ingr = 'No'
        style = ' style="color:gray"'
    else:
        have_ingr = 'Yes'
        style = ''

    print >>fp, """  <tr%s>
    <td>%s</td>
    <td>%s</td>
  </tr>
""" % (style, recipe.name, have_ingr)

print >>fp, "</table>"
print >>fp, footer
fp.close()

