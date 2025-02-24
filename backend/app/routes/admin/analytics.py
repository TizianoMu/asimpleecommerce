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
    Returns analytics data as JSON, including products per category and price ranges.
    """
    try:
        products = Product.query.all()
        categories = Category.query.all()

        if not products or not categories:
            return jsonify({"error": "No products or categories found."}), 404

        products_df = pd.DataFrame([p.__dict__ for p in products])
        categories_df = pd.DataFrame([c.__dict__ for c in categories])

        categories_df = categories_df.rename(columns={'id': 'category_id'})

        try:
            products_df = products_df.rename(columns={'category_id': 'category_id'}).merge(
                categories_df, on='category_id', suffixes=('_product', '_category')
            )
        except KeyError as e:
            return jsonify({"error": f"Key error during DataFrame merge: {str(e)}. Ensure 'category_id' exists in both DataFrames."}), 500

        products_per_category = products_df.groupby('name_category')['name_product'].count().to_dict()

        # Calculate products by price range
        bins = [0, 10, 25, 50, float('inf')]
        labels = ['< 10€', '10€ - 25€', '25€ - 50€', '> 50€']
        products_df['price_range'] = pd.cut(products_df['price'], bins=bins, labels=labels, right=False)
        products_per_price_range = products_df['price_range'].value_counts().sort_index().to_dict()

        analytics_data = {
            "products_per_category": products_per_category,
            "products_per_price_range": products_per_price_range,
        }

        return jsonify(analytics_data), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred during analytics generation: {str(e)}"}), 500
    except pd.errors.EmptyDataError as e:
        return jsonify({"error": f"Error during DataFrame creation: {str(e)}"}), 500
    except AttributeError as e:
        return jsonify({"error": f"Attribute error during query or DataFrame manipulation: {str(e)}"}), 500
    except TypeError as e:
        return jsonify({"error": f"Type error during data processing: {str(e)}"}), 500