# admin/customers.py
from flask import render_template, request, jsonify, url_for, flash, redirect
from flask_jwt_extended import jwt_required
from ...models import db, Customer
from . import admin_bp
from .schemas import CustomerSchema

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
        result = CustomerSchema(many=True).dump(customers) #use marshmallow to serialize

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


@admin_bp.route("/edit_customer", methods=["GET", "POST"])
@jwt_required()
def edit_customer():
    id_str = request.args.get('id')
    if id_str:
        try:
            id = int(id_str)
            customer = Customer.query.filter_by(id=id).first()

            if customer:
                result = CustomerSchema(many=False).dump(customer)
                response = jsonify({"customer": result})
                return response
            else:
                return jsonify({"error": "Customer not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid customer ID"}), 400
    else:
        return jsonify({"error": "Customer ID not provided"}), 400