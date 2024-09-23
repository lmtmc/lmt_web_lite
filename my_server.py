import dash
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin
import dash_bootstrap_components as dbc
from datetime import datetime
from config_loader import load_config
try :
    config = load_config()
except Exception as e:
    print(f"Error loading configuration: {e}")

server = Flask(__name__)
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI='sqlite:///users.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

prefix = config['path']['prefix']
db = SQLAlchemy(server)
# enable running the Dash app on the Flask server
app = dash.Dash(__name__, server=server,
                url_base_pathname=prefix,
                external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP],
                meta_tags=[
                    {'charset': 'utf-8'},
                    {'name': 'viewport',
                     'content': 'width=device-width, initial-scale=1, shrink-to-fit=yes'},
                ],
                prevent_initial_callbacks="initial_duplicate",
                suppress_callback_exceptions=True,
                )

login_manager = LoginManager(server)
login_manager.login_view = f'{prefix}/login'


# Create User class with UserMixin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    jobs = db.relationship('Job', backref="user", lazy=True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
        self.email = email

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    session = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.String(50), nullable=False, default=datetime.utcnow)
    username = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)

    def __init__(self, title, session, create_time, username):
        self.title = title
        self.session = session
        self.create_time = create_time
        self.username = username

with server.app_context():
    db.create_all()


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
