from flask import render_template, request, redirect, url_for
from app import db


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("base.html")

    @app.route("/about")
    def about():
        return "About Page"