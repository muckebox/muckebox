from base import Base
from file import File
from artist import Artist
from album import Album

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Track(Base):
    __tablename__ = 'tracks'

    __private__ = (
        'stringid',
        'directory',
        'bits_per_sample',
        'sample_rate'
        )

    id = Column(Integer, primary_key = True)
    stringid = Column(String, index = True, unique = True)
    directory = Column(String, index = True)

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
    bits_per_sample = Column(Integer)
    sample_rate = Column(Integer)
