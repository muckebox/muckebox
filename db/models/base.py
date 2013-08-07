from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def from_dict(self, values):
    for col in self.__table__.columns:
        if col.name in values:
            setattr(self, col.name, values[col.name])

def to_dict(self):
    column_names = set([ col.name for col in self.__table__.columns ])
    exposed_names = column_names - self.__private__ 

    return { column: getattr(self, column) for column in exposed_names }

Base.__private__ = set()
Base.from_dict = from_dict
Base.to_dict = to_dict
