from base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key = True)

    path = Column(String, index = True, unique = True)
    mtime = Column(Integer)

    tracks = relationship('Track', backref = 'file', cascade = 'all, delete, delete-orphan')

