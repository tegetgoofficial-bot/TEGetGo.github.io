from flask import Flask, render_template, request, redirect, make_response, abort, session, url_for
from flask_cors import CORS
from urllib.parse import urlparse, urljoin
import user_management as dbHandler
import html
import os
import bcrypt

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# Enable CORS to allow cross-origin requests (needed for CSRF demo in Codespaces)
app.config["SECRET_KEY"] = os.urandom(32)
app.config["WTF_CSRF_TIME_LIMIT"] = 3600 # Expiring csrf tokens every 1 minutes
app.config['TEMPLATES_AUTO_RELOAD'] = True # Auto reload every time an app route is being called
csrf = CSRFProtect(app)


if __name__ == "__main__":# This part check if the code runs on it self
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)