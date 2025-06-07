from flask import render_template, request, redirect, url_for, jsonify, session
from app.services.calculation_service import ExcelCalculationService
from app.repositories.repositories import ExcelFileRepository, CalculationRepository
from functools import wraps

from app import db
from app.models import User

# Initialize the file repository (set your upload folder path)
file_repo = ExcelFileRepository(upload_folder="uploads")
calc_repo = CalculationRepository()
excel_service = ExcelCalculationService()


# Decorator to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # If the user is not logged in, redirect to the login page
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def register_routes(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            data = request.form
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            # Validate fields
            if not username or not email or not password:
                return jsonify({"error": "All fields are required"}), 400

            # Check if user already exists
            if (
                User.query.filter_by(username=username).first()
                or User.query.filter_by(email=email).first()
            ):
                return jsonify({"error": "Username or Email already taken"}), 400

            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)

            # Save user to database
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("login"))
            # return jsonify({"msg": "User registered successfully!"}), 201
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            data = request.form
            username = data.get("username")
            password = data.get("password")

            # Validate user credentials
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                # Store user ID in session
                session["user_id"] = user.id
                return redirect(url_for("home"))

            return jsonify({"error": "Invalid credentials"}), 401

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("user_id", None)  # Removes user_id from the session
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def home():
        # Check if user is logged in
        # if 'user_id' not in session:
        #     return redirect(url_for('login'))  # Redirect to login page if not logged in

        # Fetch all Excel files and calculations from the database
        excel_files = file_repo.get_all()
        calculations = calc_repo.get_all()
        return render_template(
            "home.html", excel_files=excel_files, calculations=calculations
        )

    @app.route("/upload", methods=["POST"])
    @login_required  # Protect this route
    def upload():
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if not file:
            return jsonify({"error": "No file provided"}), 400

        user_id = session["user_id"]
        file_repo.save(file, user_id=user_id)

        return redirect(url_for("home"))

        # return {"msg": "File uploaded successfully"}

    @app.route("/delete/<int:file_id>", methods=["POST"])
    @login_required  # Protect this route
    def delete_file(file_id):
        # Delete the file from the database
        if file_repo.delete(file_id):
            return redirect(url_for("home"))
        return jsonify({"error": "File not found"}), 404

    @app.route("/calculate/<filename>", methods=["GET"])
    @login_required  # Protect this route
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
    @login_required  # Protect this route
    def new_calculation():
        if request.method == "GET":
            # Fetch all available Excel files for the dropdown
            excel_files = file_repo.get_all()
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
                excel_file = file_repo.get(excel_file_id)

                if not excel_file:
                    return (
                        jsonify(
                            {"error": f"Excel file with ID {excel_file_id} not found"}
                        ),
                        404,
                    )

                # Create a new Calculation instance
                new_calculation = calc_repo.create_calculation(
                    user_id=session["user_id"],
                    excel_file_id=excel_file_id,
                    calculation_name=calculation_name,
                    inputs=inputs,
                    outputs=outputs,
                )

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
    @login_required  # Protect this route
    def get_calculation_form(calculation_id):
        # Fetch the calculation from the database
        db_calculation = calc_repo.get_calculation_by_id(calculation_id)

        if not db_calculation:
            return jsonify({"error": "Calculation not found"}), 404

        # Extract the required inputs for the calculation
        required_inputs = db_calculation.inputs_list  # e.g., ["DATA!B1", "DATA!B2"]

        return render_template(
            "calculation_form.html", calculation=db_calculation, inputs=required_inputs
        )

    @app.route("/calculation/run/<int:calculation_id>", methods=["POST"])
    @login_required  # Protect this route
    def calculate_calculation(calculation_id):
        try:
            # Fetch the calculation from the database
            db_calculation = calc_repo.get_calculation_by_id(calculation_id)
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

    @app.route("/calculation/delete/<int:calculation_id>", methods=["POST"])
    @login_required
    def delete_calculation(calculation_id):
        # Fetch the calculation by ID

        calculation = calc_repo.delete(calculation_id)

        return redirect(url_for("home"))  # Redirect to the home page after deletion

    @app.errorhandler(404)
    def not_found_error(error):
        return redirect(url_for("home"))

    @app.route("/api", methods=["GET"])
    def api_home():
        db_calcs = calc_repo.get_all()
        return render_template("calculations_list.html", calculations=db_calcs)

    @app.route("/calculation/api/<int:calculation_id>", methods=["GET"])
    def api_calculate(calculation_id):
        try:
            # Fetch the calculation from the database
            db_calculation = calc_repo.get_calculation_by_id(calculation_id)
            if not db_calculation:
                return jsonify({"error": "Calculation not found"}), 404

            # Extract the inputs from the query parameters (or request body for POST requests)
            user_inputs = (
                request.args.to_dict()
            )  # Use query parameters for GET requests

            required_inputs = db_calculation.inputs_list  # e.g., ["DATA!B1", "DATA!B2"]
            if not all(input in user_inputs for input in required_inputs):
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
                f"'[{excel_file.filename}]{key.split('!')[0]}'!{key.split('!')[1]}": inputs_dict[
                    key
                ]
                for key in inputs_dict
            }

            solution = excel_service.model_calculate(xl_model, inputs=inputs_dict)
            results = {
                key: excel_service.get_cell_from_solution(
                    solution, excel_file.filename, key.split("!")[0], key.split("!")[1]
                )
                for key in outputs
            }

            # Return the results as JSON
            return jsonify(
                {
                    "calculation_id": db_calculation.id,
                    "name": db_calculation.name,
                    "inputs": inputs_dict,
                    "results": results,
                }
            )

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
