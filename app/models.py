# SQLAlchemy models

from app import db
import datetime
import json


class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    excel_file_id = db.Column(
        db.Integer, db.ForeignKey("excel_file.id"), nullable=False
    )
    inputs = db.Column(db.Text, nullable=True)  # Store as JSON strings
    outputs = db.Column(db.Text, nullable=True)  # Store as JSON strings
    status = db.Column(
        db.String(50), default="Pending"
    )  # Track the calculation status (Pending, In Progress, Completed)
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.datetime.now(datetime.timezone.utc),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )

    # Define the relationship to the ExcelFile
    excel_file = db.relationship("ExcelFile", back_populates="calculations")

    def __repr__(self):
        return f"<Calculation {self.id} for Excel File {self.excel_file_id}>"

    @property
    def inputs_list(self):
        """Deserialize the inputs JSON string to a Python list."""
        return json.loads(self.inputs) if self.inputs else []

    @inputs_list.setter
    def inputs_list(self, input_list):
        """Serialize the inputs Python list to a JSON string."""
        self.inputs = json.dumps(input_list)

    @property
    def outputs_list(self):
        """Deserialize the outputs JSON string to a Python list."""
        return json.loads(self.outputs) if self.outputs else []

    @outputs_list.setter
    def outputs_list(self, output_list):
        """Serialize the outputs Python list to a JSON string."""
        self.outputs = json.dumps(output_list)


class ExcelFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(
        db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
    )

    # Adding back_populates for the relationship with Calculations
    calculations = db.relationship(
        "Calculation", back_populates="excel_file", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ExcelFile {self.filename}>"
