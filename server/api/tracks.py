from cherrypy import expose, tools

from sqlalchemy.sql.expression import func
from db.models.track import Track
from db.db import Db

class TracksAPI(object):
    @expose
    @tools.json_out()
    def default(self, track_id = False, album = False):
        q = Db.get_session().query(Track)

        if album and album.isdigit():
            q = q.filter(Track.album_id == int(album))

        if track_id:
            if track_id == 'random':
                q = q.order_by(func.random()).limit(1)
            elif track_id.isdigit():
                q = q.filter(Track.id == int(track_id))

        return [ a.to_dict() for a in q ]
