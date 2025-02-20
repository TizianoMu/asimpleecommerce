from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from ..models import db, Customer, Product, Category
from flask_jwt_extended import jwt_required
from flask_marshmallow import Marshmallow
from marshmallow import fields

ma = Marshmallow()

class CustomerSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "created_at")

customer_schema = CustomerSchema(many=True)

class CategorySchema(ma.Schema):
    class Meta:
        fields = ("id", "name")

category_schema = CategorySchema(many=True)

class ProductSchema(ma.Schema):
    category = fields.Nested(CategorySchema(many=False))
    class Meta:
        fields = ("id", "name", "price", "category_id", "category")

product_schema = ProductSchema(many=True)

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@jwt_required()
def dashboard():
    return render_template("dashboard.html")

#START Categories
@admin_bp.route("/categories", methods=["GET", "POST"])
@jwt_required()
def categories():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        name = data.get("name")
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            return jsonify({"error": "Category already exists"}), 400
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        categories = Category.query.all()
        result = category_schema.dump(categories) #use marshmallow to serialize

        response = jsonify({
            "msg": "Category added",
            "redirect_url": url_for("admin.categories"),
            "categories": result #result is a list of dicts
        })

        return response
    
    categories = Category.query.all()
    return render_template("categories.html", categories=categories)

@admin_bp.route("/categories/delete/<int:id>")
@jwt_required()
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted!", "danger")
    return redirect(url_for("admin.categories"))

#END Categories

#START Customers
@admin_bp.route("/customers", methods=["GET", "POST"])
@jwt_required()
def customers():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        name = data.get("name")
        email = data.get("email")
        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            return jsonify({"error": "Email already exists"}), 400

        new_customer = Customer(name=name, email=email)
        db.session.add(new_customer)
        db.session.commit()
        customers = Customer.query.all()
        result = customer_schema.dump(customers) #use marshmallow to serialize

        response = jsonify({
            "msg": "Customer added",
            "redirect_url": url_for("admin.customers"),
            "customers": result #result is a list of dicts
        })

        return response

    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)

@admin_bp.route("/customers/delete/<int:id>")
@jwt_required()
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted!", "danger")
    return redirect(url_for("admin.customers"))

#END Customers

#START Products
@admin_bp.route("/products", methods=["GET", "POST"])
@jwt_required()
def products():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        name = data.get("name")
        price = float(data.get("price"))
        category_id = int(data.get("category_id"))

        new_product = Product(name=name, price=price, category_id=category_id)
        db.session.add(new_product)
        db.session.commit()
        products = Product.query.all()
        result_products = product_schema.dump(products) #use marshmallow to serialize
        categories = Category.query.all()
        result_categories = category_schema.dump(categories)

        response = jsonify({
            "msg": "Product added",
            "redirect_url": url_for("admin.products"),
            "products": result_products,
            "categories": result_categories,
        })

        return response

    products = Product.query.all()
    categories = Category.query.all()
    return render_template("products.html", products=products, categories=categories)

@admin_bp.route("/products/delete/<int:id>")
@jwt_required()
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Prodotto eliminato!", "danger")
    return redirect(url_for("admin.products"))

#END Products