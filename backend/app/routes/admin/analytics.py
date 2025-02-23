from flask import Blueprint, render_template, request, url_for, jsonify, make_response
from flask_jwt_extended import jwt_required, unset_jwt_cookies,set_refresh_cookies
import pandas as pd
from ...models import Product, Category, db

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/", methods=["GET"])
@jwt_required()
def analytics_page():
    """
    Renders the analytics page with data.
    """
    response, status_code = analytics_data()  # Get the response and status code
    if status_code == 200:
        data = response.get_json()  # Extract JSON data from the response
        return render_template("admin/analytics.html", data=data)  # Pass the JSON data to the template
    else:
        return render_template("admin/analytics.html", error=response.get_json()["error"]) #Pass the error to the template

@analytics_bp.route("/data", methods=["GET"])
@jwt_required()
def analytics_data():
    """
    Returns analytics data as JSON.
    """
    try:
        products = Product.query.all()
        categories = Category.query.all()

        products_df = pd.DataFrame([p.__dict__ for p in products])
        categories_df = pd.DataFrame([c.__dict__ for c in categories])

        # Rename 'id' in categories_df to 'category_id'
        categories_df = categories_df.rename(columns={'id': 'category_id'})

        products_df = products_df.rename(columns={'category_id': 'category_id'}).merge(categories_df, on='category_id', suffixes=('_product', '_category'))
        products_per_category = products_df.groupby('name_category')['name_product'].count().to_dict()

        analytics_data = {
            "products_per_category": products_per_category,
        }

        return jsonify(analytics_data), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred during analytics generation: {str(e)}"}), 500