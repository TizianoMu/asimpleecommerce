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

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "created_at", "updated_at", "is_active", "is_admin")

class OrderStatusSchema(ma.Schema):
    class Meta:
        fields = ("id", "status", "orders")
class OrderSchema(ma.Schema):
    customer = fields.Nested(CustomerSchema(many=False))
    orderStatus = fields.Nested(OrderStatusSchema(many=False))
    class Meta:
        fields = ("id", "customer_id", "total_amount", "status", "created_at", "updated_at", "customer", "orderStatus")

class OrderItemSchema(ma.Schema):
    product = fields.Nested(ProductSchema(many=False))
    order = fields.Nested(OrderSchema(many=False))
    class Meta:
        fields = ("id", "order_id", "product_id", "quantity", "price", "product", "order")