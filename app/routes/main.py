print(">>> LOADING main.py FROM:", __file__)
from flask import Blueprint, json, jsonify, request, render_template, redirect, abort
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse
from .. import db_mannager as dbHandler
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

@main_bp.route('/component/<path:folder>/<file>/<block>')
def get_component(folder, file, block):
    # 1. Get the raw string
    props_json = request.args.get('props')

    # 2. Safety Check: If it's None or just an empty string, use "{}"
    if not props_json or props_json.strip() == "":
        props = {}
    else:
        try:
            props = json.loads(props_json)
        except json.JSONDecodeError:
            props = {} # Fallback if JSON is malformed

    template_path = f"{folder}/{file}.html"
    return render_template(template_path, content=block, row=props)


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