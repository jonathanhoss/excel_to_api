import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"  # Make sure the path is correct
    SQLALCHEMY_TRACK_MODIFICATIONS = False
