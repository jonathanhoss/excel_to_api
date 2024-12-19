from .base_repository import BaseRepository
from app.models import ExcelFile


class ExcelFileRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(ExcelFile, session)
