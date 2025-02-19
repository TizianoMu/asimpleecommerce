from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Customer, Product, Category
from flask_jwt_extended import jwt_required
admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@jwt_required()
def dashboard():
    return render_template("dashboard.html")

@admin_bp.route("/categories", methods=["GET", "POST"])
@jwt_required()
def categories():
    if request.method == "POST":
        name = request.form["name"]
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        flash("Category added!", "success")
        return redirect(url_for("admin.categories"))

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

@admin_bp.route("/customers", methods=["GET", "POST"])
@jwt_required()
def customers():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        new_customer = Customer(name=name, email=email)
        db.session.add(new_customer)
        db.session.commit()
        flash("Customer added!", "success")
        return redirect(url_for("admin.customers"))

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

@admin_bp.route("/products", methods=["GET", "POST"])
@jwt_required()
def products():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        category_id = int(request.form["category_id"])

        new_product = Product(name=name, price=price, category_id=category_id)
        db.session.add(new_product)
        db.session.commit()
        flash("Prodotto aggiunto con successo!", "success")
        return redirect(url_for("admin.products"))

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
