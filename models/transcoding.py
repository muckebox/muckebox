from base import Base

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum

class Transcoding(Base):
    __tablename__ = 'transcodings'

    id = Column(Integer, primary_key = True)

    source_path = Column(String, index = True)

    format = Column(Enum('ogg', 'mp3', 'opus'), index = True)

    quality = Column(Integer, index = True)
    bits_per_sample = Column(Integer)
    sample_rate = Column(Integer)

    path = Column(String)
