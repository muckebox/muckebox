from cherrypy import expose, tools

from db.models import Artist
from db import Db

class ArtistsAPI(object):
    @expose
    @tools.json_out()
    def default(self, id = False):
        q = Db.get_session().query(Artist)

        if id and id.isdigit():
            q = q.filter(Artist.id == int(id))

        q = q.order_by(Artist.name)

        return [ a.to_dict() for a in q ]
        
