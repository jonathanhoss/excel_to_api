from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app():
    load_dotenv()

    app = Flask(__name__)
    # app.config.from_object("config.Config")  # Load the Config class from config.py
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///project.db"
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret-key")

    db.init_app(app)  # Initialize database

    # Import and register routes
    with app.app_context():
        print("Creating all tables...")
        # Ensure models are imported before calling create_all
        from app.models import Calculation, ExcelFile  # Import your models here

        db.create_all()  # Create the database tables

        from app.routes import register_routes

        register_routes(app)

    # Register blueprints
    # from app.blueprints.auth import auth
    # app.register_blueprint(auth)

    return app
