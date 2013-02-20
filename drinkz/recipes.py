"""
Recipe objects
"""

import db

class Recipe:
    def __init__(self, name, ingredients):
        self.name = name
        self.ingredients = ingredients

    def need_ingredients(self):
        missing = []
        for ingr in self.ingredients:
            typ, amount = ingr
            available = db.get_largest_liquor_type_amount(typ)
            needed = db.convert_to_ml(amount)
            if available < needed:
                missing.append((typ, needed - available))
        return missing

