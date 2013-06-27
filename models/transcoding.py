from base import Base

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum

class Transcoding(Base):
    __tablename__ = 'transcodings'

    id = Column(Integer, primary_key = True)

    source_path = Column(String, index = True)

    format = Column(Enum('ogg', 'mp3'), index = True)
    quality = Column(Integer, index = True)

    path = Column(String)
