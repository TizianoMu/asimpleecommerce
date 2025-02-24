from flask import Blueprint, render_template, request, jsonify, url_for, flash, redirect
from flask_jwt_extended import jwt_required
from ...models import db, Customer, Product, Category, User, Order, OrderItem, OrderStatus # Importa i modelli
from .schemas import CustomerSchema, CategorySchema, ProductSchema, UserSchema, OrderSchema, OrderItemSchema, OrderStatusSchema
from marshmallow import ValidationError
from sqlalchemy import and_
from sqlalchemy import Numeric, Float, Boolean, DateTime
from datetime import datetime
from .analytics import analytics_bp
import logging
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/<resource>", methods=["GET", "POST"])
@jwt_required()
def generic_admin_page(resource):
    """
    Handles GET and POST requests for generic admin pages.
    """
    # Check if the resource is valid
    if resource not in ["customers", "categories", "products", "users", "orders"]:
        return jsonify({"error": "Invalid resource"}), 404

    model_map = {
        "customers": Customer,
        "categories": Category,
        "products": Product,
        "users": User,
        "orders": Order,
        "orderItems": OrderItem,
        "orderStatus": OrderStatus
    }

    schema_map = {
        "customers": CustomerSchema,
        "categories": CategorySchema,
        "products": ProductSchema,
        "users": UserSchema,
        "orders": OrderSchema,
        "orderItems": OrderItemSchema,
        "orderStatus": OrderStatusSchema,
    }

    model = model_map[resource]
    schema = schema_map[resource](many=True)

    resource_info = {
        "users": {
            "form_fields": [("name", "Full Name", "text", "input"), ("email", "Email", "email", "input"), ("","","",""), ("","","",""), ("","","",""), ("is_active", "Is Active", "checkbox", "input"), ("is_admin", "Is Admin", "checkbox", "input")],
            "table_headers": ["ID", "Name", "Email", "Created At", "Updated At", "Last Login", "Is Active", "Is Admin"],
        },
        "customers": {
            "form_fields": [("name", "Full Name", "text", "input"), ("email", "Email", "email", "input")],
            "table_headers": ["ID", "Name", "Email"],
        },
        "categories": {
            "form_fields": [("name", "Category Name", "text", "input")],
            "table_headers": ["ID", "Name"],
        },
        "products": {
            "form_fields": [("name", "Product Name", "text", "input"), ("price", "Price", "number", "input"), ("category_id", "Category ID", "number", "select",[])],
            "table_headers": ["ID", "Name", "Price", "Category"],
        },
        "orders": {
            "form_fields": [("customer_id", "Customer ID", "number", "select",[]), ("total_amount", "Total Amount", "number", "input"), ("status_id", "Status", "number", "select",[]), ("","","",""), ("","","",""),("","","","")],
            "table_headers": ["ID", "Customer", "Total Amount", "Status", "Created At", "Updated At", "Items"],
        },
    }
    if resource == "products":
        categories = Category.query.all()
        category_options = [(category.id, category.name) for category in categories]
        resource_info["products"]["form_fields"][2] = ("category_id", "Category ID", "number", "select", category_options)
    if resource == "orders":
        customers = Customer.query.all()
        customer_options = [(customer.id, customer.name) for customer in customers]
        resource_info["orders"]["form_fields"][0] = ("customer_id", "Customer ID", "number", "select", customer_options)
        status = OrderStatus.query.all()
        status_options = [(stat.id, stat.status) for stat in status]
        resource_info["orders"]["form_fields"][2] = ("status_id", "Status ID", "number", "select", status_options)

    if request.method == "POST":
        try:
            # Attempt to parse JSON data from the request
            data = request.get_json()

            # Check if JSON data is present
            if not data:
                return jsonify({"error": "Invalid JSON: No data provided"}), 400

            # Create a new item from the parsed JSON data
            new_item = model(**data)

            # Add the new item to the database session
            db.session.add(new_item)

            # Commit the changes to the database
            db.session.commit()

            # Retrieve all items from the database after adding the new item
            items = model.query.all()

            # Serialize the items using the schema
            result = schema.dump(items)

            # Return success message, redirect URL, and serialized items
            return jsonify({
                "msg": f"{resource[:-1].capitalize()} added",
                "redirect_url": url_for("admin.generic_admin_page", resource=resource),
                resource: result,
            })

        except ValidationError as err:
            # Handle validation errors from Marshmallow schema
            return jsonify({"error": err.messages}), 400

        except Exception as e:
            # Handle any other exceptions that may occur
            db.session.rollback()
            return jsonify({"error": f"An error occurred during item addition: {str(e)}"}), 500

    else:
        # Handle GET requests for listing items
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        order_by = request.args.get('order_by', 'id')
        order_direction = request.args.get('order_direction', 'asc')

        # Build filters based on query parameters
        filters = []
        for field in resource_info[resource]["form_fields"]:
            filter_value = request.args.get(field[0])
            if filter_value:
                column = getattr(model, field[0])
                column_type = column.type
                if isinstance(column_type, type(db.String())):
                    filters.append(column.ilike(f"%{filter_value}%"))
                elif isinstance(column_type, Boolean):
                    if filter_value.lower() in ['true', '1', 'yes']:
                        filters.append(column == True)
                    elif filter_value.lower() in ['false', '0', 'no']:
                        filters.append(column == False)
                elif isinstance(column_type, DateTime):
                    try:
                        filters.append(column == datetime.fromisoformat(filter_value))
                    except ValueError:
                        pass
                else:
                    try:
                        filters.append(column == filter_value)
                    except ValueError:
                        pass

        # Query the database with filters and ordering
        if resource == "orders":
            query = Order.query.join(Customer, Order.customer_id == Customer.id).join(OrderStatus, Order.status_id == OrderStatus.id).add_columns(Order.id, Customer.name.label("customer_name"), Order.total_amount, Order.status_id, OrderStatus.status.label("status_name"), Order.created_at, Order.updated_at).filter(and_(*filters))

            if order_by == "status":
                order_column = OrderStatus.status
            elif order_by == "customer":
                order_column = Customer.name
            else:
                order_column = getattr(Order, order_by)

            if order_direction == 'desc':
                order_column = order_column.desc()

            query = query.order_by(order_column)

        elif resource == "products":
            query = Product.query.join(Category, Product.category_id == Category.id).add_columns(Product.id, Product.name, Product.price, Category.name.label("category_name")).filter(and_(*filters))

            order_column = getattr(Product, order_by)
            if order_direction == 'desc':
                order_column = order_column.desc()
            else:
                order_column = order_column.asc()


            query = query.order_by(order_column)
        else:
            order_column = getattr(model, order_by)
            if order_direction == 'desc':
                order_column = order_column.desc()
            else:
                order_column = order_column.asc()
            query = model.query.filter(and_(*filters)).order_by(order_column)

        # Paginate the results
        pagination = query.paginate(page=page, per_page=per_page)
        items = pagination.items

        # Modify the items for products and orders
        if resource == "products":
            items = [{"id": item.id, "name": item.name, "price": item.price, "category": item.category_name} for item in pagination.items]
        elif resource == "orders":
            #Set order items
            query = (
                Order.query
                .join(Customer, Order.customer_id == Customer.id)
                .join(OrderStatus, Order.status_id == OrderStatus.id)
                .outerjoin(OrderItem, Order.id == OrderItem.order_id)
                .outerjoin(Product, OrderItem.product_id == Product.id)
                .add_columns(
                    Order.id,
                    Customer.name.label("customer_name"),
                    Order.total_amount,
                    Order.status_id,
                    OrderStatus.status.label("status_name"),
                    Order.created_at,
                    Order.updated_at,
                    db.func.string_agg(Product.name, ', ').label("products")  # Raggruppa i prodotti nel formato richiesto
                )
                .group_by(Order.id, Customer.name, Order.total_amount, Order.status_id, OrderStatus.status, Order.created_at, Order.updated_at)
                .filter(and_(*filters))
            )

            # Order results
            if order_by == "status":
                order_column = OrderStatus.status
            elif order_by == "customer":
                order_column = Customer.name
            else:
                order_column = getattr(Order, order_by)

            if order_direction == 'desc':
                order_column = order_column.desc()

            query = query.order_by(order_column)

            #Paginate results
            pagination = query.paginate(page=page, per_page=per_page)
            items = [
                {
                    "id": item.id,
                    "customer": item.customer_name,
                    "total_amount": item.total_amount,
                    "status_id": item.status_id,
                    "status": item.status_name,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "products": item.products if item.products else "N/A"
                }
                for item in pagination.items
            ]
        # Render the template with the retrieved data
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template("admin/common_admin.html",
                items=items,
                resource=resource,
                resource_info=resource_info[resource],
                pagination=pagination,
                order_by=order_by,
                order_direction=order_direction,
                per_page=per_page,
                filters=request.args,
                axios_request=True)
        else:
            return render_template("admin/common_admin.html",
                items=items,
                resource=resource,
                resource_info=resource_info[resource],
                pagination=pagination,
                order_by=order_by,
                order_direction=order_direction,
                per_page=per_page,
                filters=request.args)

@admin_bp.route("/<resource>/delete/<int:id>", methods=["POST"])
@jwt_required()
def generic_delete(resource, id):
    """
    Deletes a specific resource item.
    """
    model_map = {
        "customers": Customer,
        "categories": Category,
        "products": Product,
        "users": User,
    }

    # Check if the resource is valid
    if resource not in model_map:
        return jsonify({"error": "Invalid resource"}), 404

    model = model_map[resource]

    # Attempt to retrieve the item, return 404 if not found
    item = model.query.get_or_404(id)

    try:
        # Check dependencies before deletion
        if resource == "categories":
            # Check if there are any products associated with this category
            if Product.query.filter_by(category_id=id).first():
                return jsonify({"error": "Cannot delete category with associated products."}), 400

        # Attempt to delete the item from the database
        db.session.delete(item)

        # Commit the deletion to the database
        db.session.commit()

        # Return success message and redirect URL
        return jsonify({
            "msg": f"{resource[:-1].capitalize()} deleted!",
            "redirect_url": url_for("admin.generic_admin_page", resource=resource),
        })

    except Exception as e:
        # Rollback database changes in case of an error
        db.session.rollback()

        # Return error message and internal server error status
        return jsonify({"error": f"An error occurred during deletion: {str(e)}"}), 500

@admin_bp.route("/edit_<resource>", methods=["GET"])
@jwt_required()
def generic_edit(resource):
    """
    Retrieves a specific resource item for editing.
    """
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

    # Check if the resource is valid
    if resource not in model_map or resource not in schema_map:
        return jsonify({"error": "Invalid resource"}), 404

    model = model_map[resource]
    schema = schema_map[resource](many=False)

    # Attempt to retrieve the ID from the query parameters
    id_str = request.args.get('id')

    if id_str:
        try:
            # Attempt to convert the ID to an integer
            id = int(id_str)
            
            # Attempt to retrieve the item from the database
            item = model.query.filter_by(id=id).first()

            if item:
                # Serialize the item using the schema
                result = schema.dump(item)
                return jsonify({resource[:-1]: result})
            else:
                # Item not found
                return jsonify({"error": f"{resource[:-1].capitalize()} not found"}), 404

        except ValueError:
            # ID is not a valid integer
            return jsonify({"error": "Invalid ID: Must be an integer"}), 400

        except Exception as e:
            # An unexpected error occurred
            return jsonify({"error": f"An error occurred during retrieval: {str(e)}"}), 500

    else:
        # ID is not provided in the query parameters
        return jsonify({"error": "ID not provided in query parameters"}), 400
    
@admin_bp.route("/<resource>/update/<int:id>", methods=["POST"])
@jwt_required()
def generic_update(resource, id):
    """
    Updates a specific resource item.
    """
    model_map = {
        "customers": Customer,
        "categories": Category,
        "products": Product,
    }

    # Check if the resource is valid
    if resource not in model_map:
        return jsonify({"error": "Invalid resource"}), 404

    model = model_map[resource]

    # Attempt to retrieve the item, return 404 if not found
    item = model.query.get_or_404(id)

    try:
        # Attempt to parse JSON data from the request
        data = request.get_json()

        # Check if JSON data is present
        if not data:
            return jsonify({"error": "Invalid JSON: No data provided"}), 400

        # Update attributes of the item with data from the request
        for key, value in data.items():
            try:
                setattr(item, key, value)
            except AttributeError:
                # Handle cases where the attribute doesn't exist on the model
                return jsonify({"error": f"Attribute '{key}' does not exist on the model"}), 400
            except ValueError as ve:
                # Handle cases where the value cannot be set due to type mismatch
                return jsonify({"error": f"Invalid value for attribute '{key}': {str(ve)}"}), 400

        # Commit changes to the database
        db.session.commit()

        # Return success message and redirect URL
        return jsonify({
            "msg": f"{resource[:-1].capitalize()} updated!",
            "redirect_url": url_for("admin.generic_admin_page", resource=resource),
        })

    except Exception as e:
        # Rollback database changes in case of an error
        db.session.rollback()

        # Return error message and internal server error status
        return jsonify({"error": f"An error occurred during update: {str(e)}"}), 500