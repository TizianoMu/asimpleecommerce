# admin/categories.py
from flask import render_template, request, jsonify, url_for, flash, redirect
from flask_jwt_extended import jwt_required
from ...models import db, Category
from . import admin_bp
from .schemas import CategorySchema

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
        result = CategorySchema(many=True).dump(categories) #use marshmallow to serialize

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


@admin_bp.route("/edit_category", methods=["GET", "POST"])
@jwt_required()
def edit_category():
    id_str = request.args.get('id')
    if id_str:
        try:
            id = int(id_str)
            category = Category.query.filter_by(id=id).first()

            if category:
                result = CategorySchema(many=False).dump(category)
                response = jsonify({"category": result})
                return response
            else:
                return jsonify({"error": "Category not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid category ID"}), 400
    else:
        return jsonify({"error": "Category ID not provided"}), 400