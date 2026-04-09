from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

# This gets the path to the 'app' folder where this file lives
base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            # Points exactly to app/templates
            template_folder=os.path.join(base_dir, 'templates'), 
            # Points exactly to app/statics
            static_folder=os.path.join(base_dir, 'statics'),
            static_url_path='/static')
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["TRAP_HTTP_EXCEPTIONS"] = True
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["DEBUG"] = True
    # app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-dev-key")
    # app.config["WTF_CSRF_TIME_LIMIT"] = 3600

    CORS(app)
    # csrf.init_app(app)

    print("Blueprint import test starting...")

    try:
        from app.routes.main import main_bp
        print("Blueprint imported successfully.")
    except Exception as e:
        print("Blueprint import FAILED:", e)
        raise

    app.register_blueprint(main_bp)
    print("Blueprint registered:", app.url_map)

    @app.errorhandler(500)
    def handle_500(e):
        import traceback
        traceback.print_exc()
        return f"<pre>{traceback.format_exc()}</pre>", 500

    return app