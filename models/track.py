from base import Base
from file import File

from sqlalchemy import Column, Integer, String, ForeignKey

class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key = True)
    stringid = Column(String, index = True, unique = True)

    file_id = Column(Integer, ForeignKey(File.id))

    title = Column(String)
    artist = Column(String, index = True)

    album = Column(String, index = True)
    albumartist = Column(String, index = True)
    date = Column(String)

    tracknumber = Column(Integer)
    discnumber = Column(Integer)

    label = Column(String)
    catalognumber = Column(String)

    length = Column(Integer)
    displayartist = Column(String, index = True)
