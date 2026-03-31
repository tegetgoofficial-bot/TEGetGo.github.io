print(">>> LOADING main.py FROM:", __file__)
from flask import Blueprint, json, make_response, jsonify, request, render_template, redirect, abort
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse
from .. import db_mannager as dbHandler
from werkzeug.utils import safe_join
import os

main_bp = Blueprint("main", __name__)

# ─── BLUEPRINT SETUP ───────────────────────────────────────────────────────────
# # main.py
# ADMIN_EMAIL = "your-private-email@gmail.com"

# @main_bp.route('/secret-gate-99') # The secret path you type in
# def admin_portal():
#     # 1. Check if the URL is the correct "Admin" domain
#     if request.host != "admin.tegetgo.com": # Or whatever your secret URL is
#         return redirect("https://tegetgo.onrender.com")

#     # # 2. Check the Identity (Assuming you have a user object)
#     # if not current_user.is_authenticated or current_user.email != ADMIN_EMAIL:
#     #     return redirect("https://tegetgo.onrender.com")

#     return render_template('admin_panel.html')


# ─── REACT COMUNICATION ───────────────────────────────────────────────────────────────────
# Render sets an 'IS_DEPLOEYD' or 'PORT' env var automatically
IS_DEV = os.environ.get('RENDER') is None 

@main_bp.context_processor
def inject_dev_mode():
    return dict(dev_mode=IS_DEV)

from flask import current_app # Add this import
from werkzeug.utils import safe_join

@main_bp.route('/component/<path:folder>/<file>/<block>')
def get_component(folder, file, block):
    # 1. Secure the path - Point to the actual app templates folder
    # This assumes your structure is: /app/templates/
    base_dir = os.path.join(current_app.root_path, 'templates')
    
    # safe_join ensures folder + file stays inside base_dir
    safe_path = safe_join(base_dir, folder, f"{file}.html")

    if not safe_path or not os.path.exists(safe_path):
        # Print for debugging so you can see where it's actually looking
        print(f"DEBUG: Looking for template at {safe_path}") 
        return "Template not found", 404

    # 2. Get the props
    props_json = request.args.get('props', '{}')
    try:
        props = json.loads(props_json)
    except:
        props = {}

    # 3. Get the relative path for Jinja
    # Jinja needs 'folder/file.html', not the full C:\... path
    jinja_path = os.path.relpath(safe_path, base_dir).replace('\\', '/')
    
    return render_template(jinja_path, content=block, props=props)

@main_bp.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response



# ─── TABLES ───────────────────────────────────────────────────────────────────
fromItem_table = dbHandler.QueryBuilder("ITEM")
fromCategories_table = dbHandler.QueryBuilder("CATEGORIES")
fromItem_Categories = dbHandler.QueryBuilder("ITEM_CATEGORIES")
# ─── ROUTES ───────────────────────────────────────────────────────────────────

@main_bp.route("/")
def home():
    print("Home route reached")
    items = dbHandler.get_list(
        fromItem_table.build()
    )
    categories = dbHandler.get_list(
        fromCategories_table.build()
    )
    return render_template("index.html", items=items, categories=categories)


@main_bp.route("/api/initial-data")
def get_initial_data():
    items = dbHandler.get_list(fromItem_table.build())
    categories = dbHandler.get_list(fromCategories_table.build())
    
    # Return raw data as a clean JSON object
    return jsonify({
        "items": items,
        "categories": categories
    })


@main_bp.route("/api/category/<int:category_id>")
def get_category_api(category_id):
    builder = dbHandler.QueryBuilder("ITEM I")
    
    # MERGED QUERY: 
    # 1. Joins to get the name of the CURRENT category (Option A)
    # 2. Uses a subquery to get ALL categories for each item (Option B)
    query = (
        builder.set_columns(
            "I.Item_ID, I.name, I.cost, I.itemDesc, I.image, I.itemLink, "
            "C.itemType AS active_category, " # Option A: Current context
            "(SELECT GROUP_CONCAT(cat.itemType, ', ') " # Option B: All tags
             "FROM CATEGORIES cat "
             "JOIN ITEM_CATEGORIES icat ON cat.Category_ID = icat.Category_ID "
             "WHERE icat.Item_ID = I.Item_ID) AS all_tags"
        )
        .join("ITEM_CATEGORIES IC", "I.Item_ID = IC.Item_ID")
        .join("CATEGORIES C", "C.Category_ID = IC.Category_ID")
        .add_where(f"C.Category_ID = {category_id}")
        .build()
    )

    items = dbHandler.get_list(query)
    
    if not items:
        return jsonify({"items": [], "category_name": "Category"})

    # Get the header name from the 'active_category' column
    display_name = items[0].get("active_category", "Category")

    return jsonify({
        "items": items,
        "category_name": display_name
    })



@main_bp.route("/go/<int:item_id>")
def redirect_link(item_id):
    results = dbHandler.get_list(
        fromItem_table
        .add_where(f"Item_ID = {item_id}")
        .build()
    )
    if not results:
        abort(404)

    item = results[0]
    parsed = urlparse(item["itemLink"])
    if parsed.scheme not in ("http", "https"):
        abort(403)

    return redirect(item["itemLink"])