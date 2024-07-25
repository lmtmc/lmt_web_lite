import dash
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin
from config import config
import dash_bootstrap_components as dbc
from datetime import datetime
#Diskcache
import diskcache
from dash.long_callback import DiskcacheLongCallbackManager
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

server = Flask(__name__)
server.config['SECRET_KEY'] = os.urandom(12)
# server.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'con')
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

prefix = config['path']['prefix']

db = SQLAlchemy(server)

# enable running the Dash app on the Flask server
app = dash.Dash(__name__, server=server,
                requests_pathname_prefix=prefix,
                external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP],
                meta_tags=[
                    {'charset': 'utf-8'},
                    {'name': 'viewport',
                     'content': 'width=device-width, initial-scale=1, shrink-to-fit=yes'},
                ],
                prevent_initial_callbacks="initial_duplicate",
                long_callback_manager=long_callback_manager
                )
app.config.suppress_callback_exceptions = True

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

    def __repr__(self):
        return f"User(id={self.username})"

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

    def __repr__(self):
        return f"Job(id={self.title})"


with server.app_context():
    db.create_all()


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
