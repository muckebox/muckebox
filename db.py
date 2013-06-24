from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.file import File
from models.track import Track
from models.base import Base

class Db:
    engine = False
    session_maker = False

    def __init__(self, path = False):
        if path:
            uri = 'sqlite:///%s/muckebox.db' % (path)
                        
            Db.engine = create_engine(uri)
            Db.session_maker = sessionmaker(bind = self.engine)

            Base.metadata.create_all(self.engine)

    @classmethod
    def get_session(cls):
        return cls.session_maker()
