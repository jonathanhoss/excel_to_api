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
        # Fetch all Excel files and calculations from the database
        excel_files = ExcelFile.query.all()
        calculations = Calculation.query.all()
        return render_template(
            "home.html", excel_files=excel_files, calculations=calculations
        )

    @app.route("/upload", methods=["POST"])
    def upload():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if not file:
            return jsonify({"error": "No file provided"}), 400
        file_repo.save(file)

        return redirect(url_for("home"))

        # return {"msg": "File uploaded successfully"}

    @app.route("/delete/<int:file_id>", methods=["POST"])
    def delete_file(file_id):
        # Delete the file from the database
        if file_repo.delete(file_id):
            return redirect(url_for("home"))
        return jsonify({"error": "File not found"}), 404

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

    @app.route("/calculation/new", methods=["GET", "POST"])
    def new_calculation():
        if request.method == "GET":
            # Fetch all available Excel files for the dropdown
            excel_files = ExcelFile.query.all()
            return render_template("new_calculation.html", excel_files=excel_files)

        if request.method == "POST":
            try:
                excel_file_id = request.form.get("excel_file_id")
                calculation_name = request.form.get("calculation_name")
                inputs = request.form.get("inputs")  # Retrieve inputs as a list
                outputs = request.form.get("outputs")  # Retrieve outputs as a list


                # Split the inputs and outputs into lists
                inputs = [cell.strip().upper() for cell in inputs.split(",")]
                outputs = [cell.strip().upper() for cell in outputs.split(",")]

                if not excel_file_id:
                    return jsonify({"error": "Excel file ID is required"}), 400

                if not isinstance(outputs, list) or not outputs:
                    return jsonify({"error": "Valid outputs are required"}), 400
                if not isinstance(inputs, list) or not inputs:
                    return jsonify({"error": "Valid inputs are required"}), 400

                # Verify that the referenced Excel file exists
                excel_file = ExcelFile.query.get(excel_file_id)  # TODO: Put in repo
                if not excel_file:
                    return (
                        jsonify(
                            {"error": f"Excel file with ID {excel_file_id} not found"}
                        ),
                        404,
                    )

                # Create a new Calculation instance
                new_calculation = Calculation(
                    excel_file_id=excel_file_id,
                    name=calculation_name,
                )

                new_calculation.inputs_list = inputs
                new_calculation.outputs_list = outputs

                # Save the calculation to the database
                db.session.add(new_calculation)
                db.session.commit()

                return redirect(url_for("home"))

            except Exception as e:
                return (
                    jsonify(
                        {
                            "error": f"An error occurred while creating the calculation: {str(e)}"
                        }
                    ),
                    500,
                )

    @app.route("/calculation/run/<int:calculation_id>", methods=["GET"])
    def get_calculation_form(calculation_id):
        # Fetch the calculation from the database
        db_calculation = Calculation.query.get(calculation_id)
        if not db_calculation:
            return jsonify({"error": "Calculation not found"}), 404

        # Extract the required inputs for the calculation
        required_inputs = db_calculation.inputs_list  # e.g., ["DATA!B1", "DATA!B2"]

        return render_template(
            "calculation_form.html", calculation=db_calculation, inputs=required_inputs
        )

    @app.route("/calculation/run/<int:calculation_id>", methods=["POST"])
    def calculate_calculation(calculation_id):
        try:
            # Fetch the calculation from the database
            db_calculation = Calculation.query.get(calculation_id)
            if not db_calculation:
                return jsonify({"error": "Calculation not found"}), 404

            # Extract the inputs from the form (request.form)
            user_inputs = request.form.to_dict()  # Convert form data to a dictionary

            # Ensure all required inputs are provided
            required_inputs = db_calculation.inputs_list  # e.g., ["DATA!B1", "DATA!B2"]
            print("INPUT", user_inputs)
            if not all(input in user_inputs for input in required_inputs):
                return (
                    jsonify({"error": f"Missing required inputs: {required_inputs}"}),
                    400,
                )

            # Validate that the user provided all required inputs
            required_inputs = db_calculation.inputs_list  # e.g., ["DATA!B1", "DATA!B2"]
            if not all(key in user_inputs for key in required_inputs):
                return (
                    jsonify({"error": f"Missing required inputs: {required_inputs}"}),
                    400,
                )

            # Prepare inputs as a dictionary for the calculation logic
            inputs_dict = {key: user_inputs[key] for key in required_inputs}

            # Load the Excel model
            excel_file = db_calculation.excel_file
            xl_model = excel_service.load_excel_model(excel_file.file_path).finish()

            # Run the calculation
            outputs = db_calculation.outputs_list  # e.g., ["DATA!B3"]
            inputs_dict = {
                f"'[{excel_file.filename}]{key.split("!")[0]}'!{key.split("!")[1]}": inputs_dict[
                    key
                ]
                for key in inputs_dict
            }  # TODO: Refactor

            print(f"Calculating inputs: {inputs_dict}")

            solution = excel_service.model_calculate(xl_model, inputs=inputs_dict)
            results = {
                key: excel_service.get_cell_from_solution(
                    solution, excel_file.filename, key.split("!")[0], key.split("!")[1]
                )
                for key in outputs
            }  # TODO: Refactor

            print(results)

            # Render the result in an HTML template
            return (
                render_template(
                    "calculation_result.html",
                    calculation=db_calculation,
                    inputs=user_inputs,
                    results=results,
                ),
                200,
            )

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
