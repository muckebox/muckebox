from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def from_dict(self, values):
    for col in self.__table__.columns:
        if col.name in values:
            setattr(self, col.name, values[col.name])

def to_dict(self):
    ret = { }
    privates = { }

    if hasattr(self, '__private__'):
        for p in self.__private__:
            privates[p] = True
    
    for col in self.__table__.columns:
        if not col.name in privates:
            ret[col.name] = getattr(self, col.name)

    return ret

Base.from_dict = from_dict
Base.to_dict = to_dict
