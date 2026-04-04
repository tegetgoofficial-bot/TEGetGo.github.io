print(">>> LOADING main.py FROM:", __file__)
from flask import Blueprint, json, make_response, jsonify, request, render_template, redirect, abort, url_for
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
fromItem_table = dbHandler.QueryBuilder("item")
fromCategories_table = dbHandler.QueryBuilder("categories")
fromMainCategories_table = dbHandler.QueryBuilder("main_categories")
fromItem_Categories = dbHandler.QueryBuilder("item_categories")
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
    main_categories = dbHandler.get_list(
        fromMainCategories_table.build()
    )
    return render_template("index.html", items=items, categories=categories, main_categories=main_categories)


@main_bp.route("/api/initial-data")
def get_initial_data():
    items = dbHandler.get_list(fromItem_table.build())
    categories = dbHandler.get_list(fromCategories_table.build())
    
    # Return raw data as a clean JSON object
    return jsonify({
        "items": items,
        "categories": categories
    })


@main_bp.route("/api/category/<path:category_id>")
def get_category_api(category_id):

    try:
        # Try to turn the input into a number
        id_num = int(category_id)
    except ValueError:
        # If it's text like "://google.com", just go home

        return redirect('/')
    # Use simple lowercase for table 'item' and alias 'i'
    builder = dbHandler.QueryBuilder("item i")
    
    query = (
        builder.set_columns(
            "i.item_id, i.name, i.cost, i.item_desc, i.image, i.item_link, "
            "c.item_type AS active_category, " 
            "(SELECT STRING_AGG(cat.item_type, ', ') "
            " FROM categories cat "
            " JOIN item_categories icat ON cat.category_id = icat.category_id "
            " WHERE icat.item_id = i.item_id) AS all_tags"
        )
        .join("item_categories ic", "i.item_id = ic.item_id")
        .join("categories c", "c.category_id = ic.category_id")
        .add_where(f"c.category_id = {id_num}")
        .build()
    )

    items = dbHandler.get_list(query)
    
    if not items:
        return jsonify({"error": "Invalid ID", "items": []}), 400

    # Get the header name from the 'active_category' column
    display_name = items[0].get("active_category", "Category") 

    return jsonify({
        "items": items,
        "category_name": display_name
    })



@main_bp.route("/go/<path:item_id>") # Changed 'int' to 'path' to catch everything
def redirect_link(item_id):
    try:
        # Try to turn the input into a number
        id_num = int(item_id)
    except ValueError:
        # If it's text like "://google.com", just go home
        return redirect('/')
    

    results = dbHandler.get_list(
        fromItem_table
        .add_where(f"item_id = {item_id}")
        .build()
    )

    # If the ID is invalid (no results found)
    if not results:
        # Use the name the error suggested: 'main.home'
        return redirect(url_for('main.home')) 

    item = results[0]
    target_url = item.get("item_link")
    
    if not target_url:
        return redirect(url_for('main.home'))

    # Security check
    parsed = urlparse(target_url) 
    if parsed.scheme not in ("http", "https"):
        abort(403)

    return redirect(target_url, code=307)


@main_bp.app_errorhandler(404)
def handle_404(e):
    return redirect('/')

@main_bp.app_errorhandler(403)
def handle_403(e):
    return redirect('/')