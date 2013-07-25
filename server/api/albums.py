from cherrypy import expose, tools

from models.album import Album
from utils.db import Db

class AlbumsAPI(object):
    @expose
    @tools.json_out()
    def default(self, album_id = False, artist = False):
        q = Db.get_session().query(Album)

        if artist and artist.isdigit():
            q = q.filter(Album.artist_id == int(artist))

        if album_id and album_id.isdigit():
            q = q.filter(Album.id == int(album_id))

        return [ a.to_dict() for a in q ]
