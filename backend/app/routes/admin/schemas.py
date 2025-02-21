#admin/schemas.py
from flask_marshmallow import Marshmallow
from marshmallow import fields

ma = Marshmallow()

class CustomerSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "created_at")

class CategorySchema(ma.Schema):
    class Meta:
        fields = ("id", "name")

class ProductSchema(ma.Schema):
    category = fields.Nested(CategorySchema(many=False))
    class Meta:
        fields = ("id", "name", "price", "category_id", "category")