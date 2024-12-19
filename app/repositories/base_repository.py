class BaseRepository:
    def __init__(self, model, session):
        self.model = model
        self.session = session

    def add(self, entity):
        self.session.add(entity)

    def get(self, entity_id):
        return self.session.query(self.model).get(entity_id)

    def list(self):
        return self.session.query(self.model).all()

    def delete(self, entity):
        self.session.delete(entity)
