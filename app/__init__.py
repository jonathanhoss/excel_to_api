from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Load the Config class from config.py
    db.init_app(app)  # Initialize database

    # Import and register routes
    with app.app_context():
        from app.routes import register_routes
        register_routes(app)

    # Register blueprints
    # from app.blueprints.auth import auth
    # app.register_blueprint(auth)

    return app
