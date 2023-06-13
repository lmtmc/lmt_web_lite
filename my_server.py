# Dash app initialization
import dash
# User management initialization
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin
from config import config
import dash_bootstrap_components as dbc
from datetime import datetime
from flask_migrate import Migrate

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {
            'charset': 'utf-8',
        },
        {
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1, shrink-to-fit=no'
        }
    ]
)
server = app.server

app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# server.debug = True
# server.port = '8050'
# update SQLAIchemy database URI
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI=config.get('database', 'con'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
# initializing the database extension with flask application
db = SQLAlchemy()
db.init_app(server)
migrate = Migrate(server, db)

# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


# Create User class with UserMixin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    jobs = db.relationship('Job', backref="user", lazy=True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = generate_password_hash(password, method='sha256')
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
