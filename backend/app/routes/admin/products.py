# admin/products.py
from flask import render_template, request, jsonify, url_for, flash, redirect
from flask_jwt_extended import jwt_required
from ...models import db, Product, Category
from . import admin_bp
from .schemas import ProductSchema, CategorySchema

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
        result_products = ProductSchema(many=True).dump(products) #use marshmallow to serialize
        categories = Category.query.all()
        result_categories = CategorySchema(many=True).dump(categories)

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

@admin_bp.route("/edit_product", methods=["GET", "POST"])
@jwt_required()
def edit_product():
    id_str = request.args.get('id')
    if id_str:
        try:
            id = int(id_str)
            product = Product.query.filter_by(id=id).first()

            if product:
                result = ProductSchema(many=False).dump(product)  # Serializza il prodotto con ProductSchema
                response = jsonify({"product": result})
                return response
            else:
                return jsonify({"error": "Product not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid product ID"}), 400
    else:
        return jsonify({"error": "Product ID not provided"}), 400