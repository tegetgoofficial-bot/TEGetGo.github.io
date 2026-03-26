print(">>> LOADING main.py FROM:", __file__)
from flask import Blueprint, request, render_template, redirect, abort
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse
from .. import db_mannager as dbHandler
import os

main_bp = Blueprint("main", __name__)

# ─── REACT COMUNICATION ───────────────────────────────────────────────────────────────────
# Render sets an 'IS_DEPLOEYD' or 'PORT' env var automatically
IS_DEV = os.environ.get('RENDER') is None 

@main_bp.context_processor
def inject_dev_mode():
    return dict(dev_mode=IS_DEV)

# The <path:folder> allows for subfolders like 'layouts/partials'
@main_bp.route('/component/<path:folder>/<file>/<block>')
def get_component(folder, file, block):
    template_path = f"{folder}/{file}.html"

    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest' and os.environ.get('RENDER'):
         abort(404) 
    
    # We pass 'block' as the 'content' variable for your Jinja logic
    return render_template(template_path, content=block)

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@main_bp.route("/")
def home():
    print("Home route reached")
    items = dbHandler.get_list(
        dbHandler.QueryBuilder("ITEM").build()
    )
    categories = dbHandler.get_list(
        dbHandler.QueryBuilder("CATEGORIES").build()
    )
    return render_template("index.html", items=items, categories=categories)


@main_bp.route("/category/<int:category_id>")
def category(category_id):
    items = dbHandler.get_list(
        dbHandler.QueryBuilder("ITEM")
        .set_where(f"Item_ID IN (SELECT Item_ID FROM ITEM_CATEGORIES WHERE Category_ID = {category_id})")
        .build()
    )
    categories = dbHandler.get_list(
        dbHandler.QueryBuilder("CATEGORIES").build()
    )
    return render_template("index.html", items=items, categories=categories)


@main_bp.route("/go/<int:item_id>")
def redirect_link(item_id):
    results = dbHandler.get_list(
        dbHandler.QueryBuilder("ITEM")
        .set_where(f"Item_ID = {item_id}")
        .build()
    )
    if not results:
        abort(404)

    item = results[0]
    parsed = urlparse(item["Item_AffiliateLink"])
    if parsed.scheme not in ("http", "https"):
        abort(403)

    return redirect(item["Item_AffiliateLink"])