from flask import render_template, request, redirect, url_for, jsonify
from app import db
from app.services.calculation_service import ExcelCalculationService
from app.repositories.file_repository import ExcelFileRepository
from app.models import Calculation, ExcelFile

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

        mdl = excel_service.load_excel_model("test_a.xlsx").finish()
        return {"msg": str(excel_service.model_calculate(mdl))}

    @app.route("/upload", methods=["POST"])
    def upload():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if not file:
            return jsonify({"error": "No file provided"}), 400
        file_repo.save(file)

        return {"msg": "File uploaded successfully"}

    @app.route("/list-files", methods=["GET"])
    def list_files():
        return jsonify(str(file_repo.list_files()))

    @app.route("/calculate/<filename>", methods=["GET"])
    def calculate_excel(filename):
        # Get the Excel file from the database using the filename
        excel_file = file_repo.get_file_by_name(filename)

        if not excel_file:
            return jsonify({"error": "File not found"}), 404

        try:
            # Use the formulas library to process the file
            fpath = excel_file.file_path  # Get the file path from the database

            xlm = excel_service.load_excel_model(fpath).finish()

            # Calculate the model
            xl_model = excel_service.model_calculate(xlm)

            # Return a success message
            return (
                jsonify(
                    {
                        "msg": f"File {filename} calculated successfully!",
                        "output": str(xl_model),
                    }
                ),
                200,
            )

        except Exception as e:
            return (
                jsonify(
                    {"error": f"An error occurred while processing the file: {str(e)}"}
                ),
                500,
            )
        
    @app.route("/calculation/create", methods=["POST"])
    def create_calculation():
        try:
            # Parse and validate the JSON request body
            data = request.get_json()
            if not data:
                return jsonify({"error": "No input data provided"}), 400

            # Extract fields
            excel_file_id = data.get("excel_file_id")
            inputs = data.get("inputs")
            outputs = data.get("outputs")

            if not excel_file_id:
                return jsonify({"error": "Excel file ID is required"}), 400

            if not isinstance(outputs, list) or not outputs:
                return jsonify({"error": "Valid outputs are required"}), 400
            if not isinstance(inputs, list) or not inputs:
                return jsonify({"error": "Valid inputs are required"}), 400

            # Verify that the referenced Excel file exists
            excel_file = ExcelFile.query.get(excel_file_id) # TODO: Put in repo
            if not excel_file:
                return jsonify({"error": f"Excel file with ID {excel_file_id} not found"}), 404

            # Create a new Calculation instance
            new_calculation = Calculation(
                excel_file_id=excel_file_id,
            )

            new_calculation.inputs_list = inputs
            new_calculation.outputs_list = outputs

            # Save the calculation to the database
            db.session.add(new_calculation)
            db.session.commit()

            return jsonify({
                "msg": "Calculation created successfully",
                "calculation_id": new_calculation.id
            }), 201

        except Exception as e:
            return jsonify({"error": f"An error occurred while creating the calculation: {str(e)}"}), 500


    @app.route("/calculation/run/<int:calculation_id>", methods=["POST"])
    def calculate_calculation(calculation_id):
        try:
            # Fetch the calculation from the database
            db_calculation = Calculation.query.get(calculation_id)
            if not db_calculation:
                return jsonify({"error": "Calculation not found"}), 404

            # Parse the input values from the request body
            data = request.get_json()
            if not data or "inputs" not in data:
                return jsonify({"error": "Inputs are required"}), 400

            # Get the user-provided inputs
            user_inputs = data["inputs"]

            # Validate that the user provided all required inputs
            required_inputs = db_calculation.inputs_list  # e.g., ["DATA!B1", "DATA!B2"]
            if not all(key in user_inputs for key in required_inputs):
                return jsonify({"error": f"Missing required inputs: {required_inputs}"}), 400

            # Prepare inputs as a dictionary for the calculation logic
            inputs_dict = {key: user_inputs[key] for key in required_inputs}

            # Load the Excel model
            excel_file = db_calculation.excel_file
            xl_model = excel_service.load_excel_model(excel_file.file_path).finish()

            # Run the calculation
            outputs = db_calculation.outputs_list  # e.g., ["DATA!B3"]
            inputs_dict = {f"'[{excel_file.filename}]{key.split("!")[0]}'!{key.split("!")[1]}": inputs_dict[key] for key in inputs_dict} # TODO: Refactor

            print(f"Calculating inputs: {inputs_dict}")

            solution = excel_service.model_calculate(xl_model, inputs=inputs_dict)
            results = {key: excel_service.get_cell_from_solution(solution, excel_file.filename, key.split("!")[0], key.split("!")[1]) for key in outputs} # TODO: Refactor

            print(results)

            # Return the results to the user
            return jsonify({
                "msg": f"Calculation {calculation_id} executed successfully",
                "results": results
            }), 200

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500