print(">>> LOADING main.py FROM:", __file__)
from flask import Blueprint, render_template, redirect, abort
from urllib.parse import urlparse
from .. import db_mannager as dbHandler

main_bp = Blueprint("main", __name__)

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