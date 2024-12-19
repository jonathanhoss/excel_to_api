from .base_repository import BaseRepository
from app.models import Mapping


class MappingRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(Mapping, session)

    def find_by_file_id(self, file_id):
        return self.session.query(self.model).filter_by(file_id=file_id).all()
