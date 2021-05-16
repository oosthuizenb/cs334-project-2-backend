from flask import Flask
from flask_cors import CORS
from . import config

from .database.models import db

app = Flask(__name__)


def create_app():
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['SECRET_KEY'] = 'SUPERSECRET'
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

    from .graphs import graphs
    app.register_blueprint(graphs, url_prefix='/graphs')

    from .employees import employees
    app.register_blueprint(employees, url_prefix='/employees')

    db.create_all(app=app)

    return app
