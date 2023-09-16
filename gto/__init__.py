import os
from flask import Flask
import bfa
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from . import __base__ as base


login_manager = LoginManager()
login_manager.session_protection = "strong"


app = Flask(__name__)


@app.context_processor
def bfa_flask():
    return bfa.templatetags.bfa.fingerprint_input()


app.config["UPLOAD_EXTENSIONS"] = ['.txt', '.pdf']
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'
os.environ["OAUTH_RELAX_TOKEN_SCOPE"] = '1'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 100
app.config["SECRET_KEY"] = base.configdict.get("SECRET_KEY")
app.config["UPLOAD_PATH"] = base.configdict.get("FILE_UPLOAD_PATH")
app.config["SQLALCHEMY_DATABASE_URI"] = base.configdict.get("SQL_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECURITY_PASSWORD_SALT"] = base.configdict.get(
    "SECURITY_PASSWORD_SALT")

db = SQLAlchemy(app)
Migrate(app, db)
login_manager.init_app(app)

login_manager.login_view = 'login'
