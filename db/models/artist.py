from base import Base

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

class Artist(Base):
    __tablename__ = 'artists'
    
    id = Column(Integer, primary_key = True)

    name = Column(String, index = True, unique = True)
