from app.models import ExcelFile
from werkzeug.utils import secure_filename
import os
from app import db


class ExcelFileRepository:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)  # Ensure the folder exists

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