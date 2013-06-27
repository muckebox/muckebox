from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.file import File
from models.track import Track
from models.album import Album
from models.artist import Artist

from models.base import Base

class Db(object):
    engine = False
    session_maker = False

    @classmethod
    def open(cls, path, verbose = False):
        uri = 'sqlite:///%s/muckebox.db' % (path)
                        
        Db.engine = create_engine(uri, echo = verbose)
        Db.session_maker = sessionmaker(bind = cls.engine)

        Base.metadata.create_all(cls.engine)

    @classmethod
    def get_session(cls):
        return cls.session_maker()
