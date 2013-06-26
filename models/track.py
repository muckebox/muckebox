from base import Base
from file import File
from artist import Artist
from album import Album
from transcoding import Transcoding

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key = True)
    stringid = Column(String, index = True, unique = True)

    file_id = Column(Integer, ForeignKey(File.id))

    title = Column(String)

    album_id = Column(Integer, ForeignKey(Album.id))
    artist_id = Column(Integer, ForeignKey(Artist.id))

    displayartist = Column(String, index = True)

    date = Column(String)

    tracknumber = Column(Integer)
    discnumber = Column(Integer)

    label = Column(String)
    catalognumber = Column(String)

    length = Column(Integer)

    transcodings = relationship('Transcoding', backref = 'track', cascade = 'all, delete, delete-orphan')
