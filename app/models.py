# SQLAlchemy models

from app import db
import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class ExcelFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(
        db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
    )

    def __repr__(self):
        return f"<ExcelFile {self.filename}>"


class Mapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("excel_file.id"), nullable=False)
    input_cell = db.Column(db.String(10), nullable=False)
    output_cell = db.Column(db.String(10), nullable=False)
