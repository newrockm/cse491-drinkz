"""
Database functionality for drinkz information.

Recipes are stored as a dict to make it easy to find recipes by name.
"""

from cPickle import dump, load

# private singleton variables at module level
_bottle_types_db = set()
_inventory_db = {}
_recipe_db = {}

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db, _recipe_db
    _bottle_types_db = set()
    _inventory_db = {}
    _recipe_db = {}

def save_db(filename):
    fp = open(filename, 'wb')

    tosave = (_bottle_types_db, _inventory_db, _recipe_db)
    dump(tosave, fp)

    fp.close()

def load_db(filename):
    global _bottle_types_db, _inventory_db, _recipe_db
    fp = open(filename, 'rb')

    loaded = load(fp)
    (_bottle_types_db, _inventory_db, _recipe_db) = loaded

    fp.close()

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass

class DuplicateRecipeName(Exception):
    pass

def add_bottle_type(mfg, liquor, typ):
    "Add the given bottle type into the drinkz database."
    _bottle_types_db.add((mfg, liquor, typ))

def _check_bottle_type_exists(mfg, liquor):
    for (m, l, _) in _bottle_types_db:
        if mfg == m and liquor == l:
            return True

    return False

def get_bottle_types():
    for bottle in _bottle_types_db:
        yield bottle

def add_to_inventory(mfg, liquor, amount):
    "Add the given liquor/amount to inventory."
    if not _check_bottle_type_exists(mfg, liquor):
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

    qty = convert_to_ml(amount)

    # if the mfg, liquor exists, add to the total amount.  Otherwise, create.
    try:
        _inventory_db[(mfg, liquor)] += qty
    except KeyError:
        _inventory_db[(mfg, liquor)] = qty


def check_inventory(mfg, liquor):
    return (mfg, liquor) in _inventory_db

def check_inventory_for_type(typ):
    found_bottles = []
    for (mfg, liquor, t) in _bottle_types_db:
        # bottle type is the third field
        if t == typ:
            try:
                # add each bottle of this type to the list
                found_bottles.append((mfg, liquor))
            except KeyError:
                # bottle doesn't exist?  oh well.
                pass
    return found_bottles
    
def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    try:
        qty = _inventory_db[(mfg, liquor)]
    except KeyError:
        raise Exception("(%s, %s) not in inventory" % (mfg, liquor))

    return round(qty, 2)

def get_largest_liquor_type_amount(typ):
    "Return the amount of alcohol of this type from the largest bottle in ml."
    # start with an empty bottle
    qty = [0]
    for bottle in check_inventory_for_type(typ):
        qty.append(_inventory_db[bottle])
    return max(qty)

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for (m, l) in _inventory_db:
        yield m, l

# recipe functions

def add_recipe(r):
    if _recipe_db.has_key(r.name):
        err = 'Recipe "%s" already exists.' % r.name
        raise DuplicateRecipeName(err)
    
    _recipe_db[r.name] = r

def get_recipe(name):
    try:
        return _recipe_db[name]
    except KeyError:
        return None

def get_all_recipes():
    for r in _recipe_db.itervalues():
        yield r

# utility functions

def convert_to_ml(amount):
    try:
        qty, unit = amount.split()
        qty = float(qty)
    except ValueError:
        raise ValueError("Invalid amount '%s'" % amount)

    conversion = {
        'ml': 1,
        'oz': 29.5735,
        'gallon': 29.5735 * 128,
        'gallons': 29.5735 * 128,
        'liter': 1000,
        'liters': 1000
    }

    try:
        return qty * conversion[unit]
    except KeyError:
        raise ValueError("Invalid unit in amount '%s'" % amount)

