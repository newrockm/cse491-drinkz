"""
Miscellaneous professor tests.
"""

import sys
sys.path.insert(0, 'bin/') # allow _mypath to be loaded; @CTB hack hack hack
import os

from . import db, load_bulk_data
from cStringIO import StringIO
import imp

def test_get_liquor_amount_gallon():
    db._reset_db()

    db.add_bottle_type('Johnnie Walker', 'Black Label', 'blended scotch')
    
    data = "Johnnie Walker,Black Label,1 gallon"
    fp = StringIO(data)                 # make this look like a file handle
    n = load_bulk_data.load_inventory(fp)

    amount = db.get_liquor_amount('Johnnie Walker', 'Black Label')
    assert amount == 3785.41, amount

def test_uniqify_inventory():
    """
    Ensure that get_liquor_inventory doesn't return duplicates.
    """
    db._reset_db()

    db.add_bottle_type('Johnnie Walker', 'Black Label', 'blended scotch')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '1000 ml')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '500 ml')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '25 ml')

    uniq = set()
    for mfg, liquor in db.get_liquor_inventory():
        assert (mfg, liquor) not in uniq, "dup: %s, %s" % (mfg, liquor)
        uniq.add((mfg, liquor))

    assert len(uniq) == 1, "should only be one mfg/liquor in inventory"

def test_script_load_liquor_inventory():
    db._reset_db()

    scriptpath = 'bin/load-liquor-inventory'
    module = imp.load_source('llt', scriptpath)
    exit_code = module.main([scriptpath, 'test-data/bottle-types-data-1.txt',
                             'test-data/inventory-data-1.txt'])

    assert exit_code == 0, 'non zero exit code %s' % exit_code
    amount = db.get_liquor_amount('Johnnie Walker', 'Black Label')
    # fixed to match the test data
    assert amount == 1234

def test_for_properly_named_grab_script():
    # HW 4.6.
    assert os.path.exists('./grab-page')

def test_for_properly_named_app():
    # HW 4.2
    assert os.path.exists('./drinkz/app.py')

def test_for_properly_named_run_script():
    # HW 4.2(a)
    assert os.path.exists('./bin/run-web')

def test_for_properly_named_saveload_script():
    # HW 4.2(a)
    assert os.path.exists('./bin/make-test-database')

def test_bulk_load_bottle_types_badformat():
    db._reset_db()

    data = "#comment\n \na,b\nJohnnie Walker,Black Label,blended scotch\n\n"
    fp = StringIO(data)                 # make this look like a file handle
    n = load_bulk_data.load_bottle_types(fp)

    assert n == 1, n
    assert db._check_bottle_type_exists('Johnnie Walker', 'Black Label')
