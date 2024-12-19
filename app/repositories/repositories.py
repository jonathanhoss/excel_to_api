from app.models import ExcelFile, Calculation
from werkzeug.utils import secure_filename
import os
from app import db


class ExcelFileRepository:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)  # Ensure the folder exists

    def get_all(self):
        return ExcelFile.query.all()

    def save(self, file):
        filename = secure_filename(file.filename)
        file_path = os.path.join(self.upload_folder, filename)

        # Save the file to the filesystem
        file.save(file_path)

        # Save file metadata in the database
        excel_file = ExcelFile(filename=filename, file_path=file_path)
        db.session.add(excel_file)
        db.session.commit()

        return file_path

    def get(self, file_id):
        return ExcelFile.query.get(file_id)

    def delete(self, file_id: int):
        excel_file = ExcelFile.query.get(file_id)
        if excel_file:
            db.session.delete(excel_file)
            db.session.commit()
            return True
        return False

    def list_files(self):
        # Query all files from the database
        files = ExcelFile.query.all()

        # Prepare the list of files as a list of dictionaries
        file_list = []
        for file in files:
            file_info = {
                "id": file.id,
                "filename": file.filename,
                "file_path": file.file_path,
                "uploaded_at": file.uploaded_at,
            }
            file_list.append(file_info)

        return file_list

    def get_file_by_name(self, filename):
        # Retrieve the file metadata by filename from the database
        return ExcelFile.query.filter_by(filename=filename).first()


class CalculationRepository:
    def get_all(self):
        return Calculation.query.all()

    def get_calculation_by_id(self, calc_id):
        return Calculation.query.get(calc_id)

    def create_calculation(
        self, excel_file_id, calculation_name: str, inputs: list, outputs: list
    ):
        # Create a new Calculation instance
        new_calculation = Calculation(
            excel_file_id=excel_file_id,
            name=calculation_name,
        )

        # Set the inputs and outputs lists
        new_calculation.inputs_list = inputs
        new_calculation.outputs_list = outputs

        # Save the calculation to the database
        db.session.add(new_calculation)
        db.session.commit()

        return new_calculation

    def update_calculation(self, calc_id, status, outputs):
        calc = self.get_calculation_by_id(calc_id)
        if calc:
            calc.status = status
            calc.outputs = outputs
            db.session.commit()
            return calc
        return None

    def delete_calculation(self, calc_id):
        calc = self.get_calculation_by_id(calc_id)
        if calc:
            db.session.delete(calc)
            db.session.commit()
            return True
        return False
