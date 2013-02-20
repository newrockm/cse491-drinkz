"""
Tests basic recipe API.
"""

import unittest
from . import db, recipes

class TestBasicRecipeStuff(unittest.TestCase):
    def setUp(self):                    # This is run once per test, before.
        db._reset_db()

    def tearDown(self):                 # This is run once per test, after.
        pass

    def test_add_recipe_1(self):
        x = list(db.get_all_recipes())
        assert not x                    # should be no recipes
        
        r = recipes.Recipe('scotch on the rocks', [('blended scotch',
                                                   '4 oz')])

        db.add_recipe(r)

        x = list(db.get_all_recipes())
        assert len(x) == 1              # should be only one recipe
        assert r in x

    def test_add_recipe_2(self):
        r = recipes.Recipe('scotch on the rocks', [('blended scotch',
                                                   '4 oz')])
        db.add_recipe(r)
            
        r2 = recipes.Recipe('scotch on the rocks', [('vodka', '4 oz')])
        try:
            db.add_recipe(r2)
            assert 0, "this is a duplicate recipe and the add should fail"
        except db.DuplicateRecipeName:
            pass                        # success, we got an exception

    def test_get_recipe_1(self):
        r = recipes.Recipe('scotch on the rocks', [('blended scotch',
                                                   '4 oz')])

        db.add_recipe(r)

        x = db.get_recipe('scotch on the rocks')
        assert x == r

    def test_get_recipe_2(self):
        x = db.get_recipe('scotch on the rocks')
        assert not x, x                    # no such recipe

class TestIngredients(object):
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

    def test_need_ingredients_1(self):
        r = recipes.Recipe('scotch on the rocks', [('blended scotch',
                                                   '4 oz')])

        x = r.need_ingredients()
        assert not x, x

    def test_need_ingredients_2(self):
        r = recipes.Recipe('vodka martini', [('unflavored vodka', '6 oz'),
                                            ('vermouth', '1.5 oz')])

        x = r.need_ingredients()
        assert not x, x

    def test_need_ingredients_3(self):
        r = recipes.Recipe('vomit inducing martini', [('orange juice',
                                                      '6 oz'),
                                                     ('vermouth',
                                                      '1.5 oz')])

        missing = r.need_ingredients()
        assert missing
        assert len(missing) == 1

        assert missing[0][0] == 'orange juice', missing
        assert round(missing[0][1], 1) == 177.4, missing   # 6 oz in ml

    def test_generic_replacement(self):
        r = recipes.Recipe('whiskey bath', [('blended scotch', '2 liter')])

        missing = r.need_ingredients()
        assert not missing, missing

    def test_generic_replacement_fail(self):
        # the logic here is a bit tricky -- we need AT LEAST 1 liter of
        # blended scotch for this recipe, because we have 5 liter of
        # Uncle Herman's moonshine.
        
        r = recipes.Recipe('whiskey bath', [('blended scotch', '6 liter')])

        missing = r.need_ingredients()
        assert missing == [('blended scotch', 1000.0)], missing

    def test_generic_replacement_no_mix(self):
        # the logic here is again a bit tricky -- we technically don't
        # need any blended scotch, if we were to combine Uncle Herman's
        # moonshine with Johnnie Walker Black Label.  But we don't want
        # to allow mixing of bottles, in general, because that's
        # just icky.  So we report back that we need at least half a liter
        # of blended scotch.

        r = recipes.Recipe('whiskey bath', [('blended scotch', '5.5 liter')])

        missing = r.need_ingredients()
        assert missing == [('blended scotch', 500.0)]
