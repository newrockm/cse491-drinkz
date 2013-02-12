"""
Database functionality for drinkz information.
"""

# private singleton variables at module level
_bottle_types_db = set()
_inventory_db = {}

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db
    _bottle_types_db = set()
    _inventory_db = {}

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass

def add_bottle_type(mfg, liquor, typ):
    "Add the given bottle type into the drinkz database."
    _bottle_types_db.add((mfg, liquor, typ))

def _check_bottle_type_exists(mfg, liquor):
    for (m, l, _) in _bottle_types_db:
        if mfg == m and liquor == l:
            return True

    return False

def add_to_inventory(mfg, liquor, amount):
    "Add the given liquor/amount to inventory."
    if not _check_bottle_type_exists(mfg, liquor):
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

    # this will also catch too many fields
    try:
        qty, unit = amount.split()
        qty = float(qty)
    except ValueError:
        raise ValueError("Invalid amount '%s'" % amount)

    # we only accept ml or oz
    if unit == 'oz':
        # 1oz = 29.5735ml (according to google calc)
        qty = qty * 29.5735

    elif unit != 'ml':
        raise ValueError("Invalid unit in amount '%s'" % amount)

    # if the mfg, liquor exists, add to the total amount.  Otherwise, create.
    try:
        _inventory_db[(mfg, liquor)] += qty
    except KeyError:
        _inventory_db[(mfg, liquor)] = qty


def check_inventory(mfg, liquor):
    return (mfg, liquor) in _inventory_db

def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    try:
        qty = _inventory_db[(mfg, liquor)]
    except KeyError:
        raise Exception("(%s, %s) not in inventory" % (mfg, liquor))

    # callers expect a string declaring ml
    return '%d ml' % round(qty)

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for (m, l) in _inventory_db:
        yield m, l
