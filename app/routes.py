from flask import render_template, request, redirect, url_for, jsonify
from app import db
from app.services.calculation_service import ExcelCalculationService
from app.repositories.file_repository import ExcelFileRepository

# Initialize the file repository (set your upload folder path)
file_repo = ExcelFileRepository(upload_folder="uploads")
excel_service = ExcelCalculationService()


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("base.html")

    @app.route("/debug")
    def debug():
        excel_service

        mdl = service.load_excel_model("test_a.xlsx").finish()
        return {
            "msg": str(service.model_calculate(mdl))
            }
    

    @app.route("/upload", methods=["POST"])
    def upload():
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files['file']
        if not file:
            return jsonify({"error": "No file provided"}), 400
        file_repo.save(file)

        return {"msg": "File uploaded successfully"}