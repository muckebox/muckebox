from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import File
from models import Track
from models import Album
from models import Artist
from models import Transcoding

from models import Base

class Db(object):
    engine = False
    session_maker = False

    @classmethod
    def open(cls, path, verbose = False):
        uri = 'sqlite:///%s' % (path)
                        
        Db.engine = create_engine(uri, echo = verbose)
        Db.session_maker = sessionmaker(bind = cls.engine)

        Base.metadata.create_all(cls.engine)

    @classmethod
    def get_session(cls):
        return cls.session_maker()
