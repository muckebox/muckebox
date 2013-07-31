from base import Base
from artist import Artist

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

class Album(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key = True)

    title = Column(String, index = True)
    artist_id = Column(Integer, ForeignKey(Artist.id))

    artist = relationship('Artist', backref = 'albums')
    tracks = relationship('Track', backref = 'album')
