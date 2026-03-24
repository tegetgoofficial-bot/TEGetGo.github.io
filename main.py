from flask import Flask, render_template, request, redirect, abort
from flask_cors import CORS
from urllib.parse import urlparse
from dotenv import load_dotenv
import user_management as dbHandler
import os

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, template_folder='templates', static_folder='statics')
CORS(app)

app.config["SECRET_KEY"] = os.urandom(32)
app.config["WTF_CSRF_TIME_LIMIT"] = 3600
app.config['TEMPLATES_AUTO_RELOAD'] = True

csrf = CSRFProtect(app)

# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
@csrf.exempt
def home():
    items = dbHandler.get_list(
        dbHandler.QueryBuilder("ITEM").build()
    )
    categories = dbHandler.get_list(
        dbHandler.QueryBuilder("CATEGORIES").build()
    )
    return render_template("index.html", items=items, categories=categories)

@app.route("/category/<int:category_id>")
@csrf.exempt
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

@app.route("/go/<int:item_id>")
@csrf.exempt
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

# Future feedback form - CSRF protected ✅
@app.route("/feedback", methods=["POST"])
def feedback():
    # CSRF token required here - not exempted!
    pass

# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)