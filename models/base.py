from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def from_dict(self, values):
    for col in self.__table__.columns:
        if col.name in values:
            setattr(self, col.name, values[col.name])

Base.from_dict = from_dict
