from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from auth import auth_ns
from exts import db
from models import User, Stats
from stats import stats_ns


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    CORS(app)
    JWTManager(app)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Stats': Stats,
            'User': User
        }

    api = Api(app, doc='/docs')
    api.add_namespace(auth_ns)
    api.add_namespace(stats_ns)

    return app
