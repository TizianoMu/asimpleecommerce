from flask import Blueprint, render_template, request, jsonify, url_for, flash, redirect
from flask_jwt_extended import jwt_required
from ...models import db, Customer, Product, Category  # Importa i modelli
from .schemas import CustomerSchema, CategorySchema, ProductSchema
from marshmallow import ValidationError
from sqlalchemy import and_
from sqlalchemy import Integer, Boolean, DateTime
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/<resource>", methods=["GET", "POST"])
@jwt_required()
def generic_admin_page(resource):
    if resource not in ["customers", "categories", "products"]:
        return jsonify({"error": "Invalid resource"}), 404

    model_map = {
        "customers": Customer,
        "categories": Category,
        "products": Product,
    }

    schema_map = {
        "customers": CustomerSchema,
        "categories": CategorySchema,
        "products": ProductSchema,
    }

    model = model_map[resource]
    schema = schema_map[resource](many=True)

    resource_info = {
        "customers": {
            "form_fields": [("name", "Full Name", "text"), ("email", "Email", "email")],
            "table_headers": ["ID", "Name", "Email"],
        },
        "categories": {
            "form_fields": [("name", "Category Name", "text")],
            "table_headers": ["ID", "Name"],
        },
        "products": {
            "form_fields": [("name", "Product Name", "text"), ("price", "Price", "number"), ("category_id", "Category ID", "number")],
            "table_headers": ["ID", "Name", "Price", "Category ID"],
        },
    }

    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON"}), 400

            new_item = model(**data)
            db.session.add(new_item)
            db.session.commit()

            items = model.query.all()
            result = schema.dump(items)

            return jsonify({
                "msg": f"{resource[:-1].capitalize()} added",
                "redirect_url": url_for("admin.generic_admin_page", resource=resource),
                resource: result,
            })
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400
    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        order_by = request.args.get('order_by', 'id')
        order_direction = request.args.get('order_direction', 'asc')
        
        order_column = getattr(model, order_by)
        if order_direction == 'desc':
            order_column = order_column.desc()
        
        filters = []
        for field in resource_info[resource]["form_fields"]:
            filter_value = request.args.get(field[0])
            if filter_value:
                column = getattr(model, field[0])
                column_type = column.type

                if isinstance(column_type, type(db.String())): # String type check
                    filters.append(column.ilike(f"%{filter_value}%"))
                elif isinstance(column_type, Integer): # Integer type check
                    try:
                        filters.append(column == int(filter_value))
                    except ValueError:
                        pass # Ignore if filter_value is not an integer
                elif isinstance(column_type, Boolean): # Boolean type check
                    if filter_value.lower() in ['true', '1', 'yes']:
                        filters.append(column == True)
                    elif filter_value.lower() in ['false', '0', 'no']:
                        filters.append(column == False)
                elif isinstance(column_type, DateTime): # DateTime type check
                    try:
                        filters.append(column == datetime.fromisoformat(filter_value))
                    except ValueError:
                        pass # Ignore if filter_value is not a valid date
                else:
                    pass # Ignore other types. You can add more type checks here if needed.

        query = model.query.filter(and_(*filters)).order_by(order_column)
        pagination = query.paginate(page=page, per_page=per_page)
        items = pagination.items

        return render_template("admin/common_admin.html",
                               items=items,
                               resource=resource,
                               resource_info=resource_info[resource],
                               pagination=pagination,
                               order_by=order_by,
                               order_direction=order_direction,
                               per_page=per_page,
                               filters=request.args)

@admin_bp.route("/<resource>/delete/<int:id>",methods=["POST"])
@jwt_required()
def generic_delete(resource, id):
    model_map = {
        "customers": Customer,
        "categories": Category,
        "products": Product,
    }
    if resource not in model_map:
        return jsonify({"error": "Invalid resource"}), 404

    model = model_map[resource]
    item = model.query.get_or_404(id)
    try:
        # check dependencies
        if resource == "categories":
            if Product.query.filter_by(category_id=id).first():
                return jsonify({"error":"Cannot delete category with associated products."}),400
        
        db.session.delete(item)
        db.session.commit()
        return jsonify({
            "msg": f"{resource[:-1].capitalize()} deleted!",
            "redirect_url": url_for("admin.generic_admin_page", resource=resource),
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/edit_<resource>", methods=["GET"])
@jwt_required()
def generic_edit(resource):
    model_map = {
        "customers": Customer,
        "categories": Category,
        "products": Product,
    }
    schema_map = {
        "customers": CustomerSchema,
        "categories": CategorySchema,
        "products": ProductSchema,
    }

    if resource not in model_map or resource not in schema_map:
        return jsonify({"error": "Invalid resource"}), 404

    model = model_map[resource]
    schema = schema_map[resource](many=False)

    id_str = request.args.get('id')
    if id_str:
        try:
            id = int(id_str)
            item = model.query.filter_by(id=id).first()
            if item:
                result = schema.dump(item)
                return jsonify({resource[:-1]: result})
            else:
                return jsonify({"error": f"{resource[:-1].capitalize()} not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid ID"}), 400
    else:
        return jsonify({"error": "ID not provided"}), 400
    
@admin_bp.route("/<resource>/update/<int:id>", methods=["POST"])
@jwt_required()
def generic_update(resource, id):
    model_map = {
        "customers": Customer,
        "categories": Category,
        "products": Product,
    }
    if resource not in model_map:
        return jsonify({"error": "Invalid resource"}), 404

    model = model_map[resource]
    item = model.query.get_or_404(id)

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        # Update attributes
        for key, value in data.items():
            setattr(item, key, value)

        db.session.commit()
        return jsonify({
            "msg": f"{resource[:-1].capitalize()} updated!",
            "redirect_url": url_for("admin.generic_admin_page", resource=resource),
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500