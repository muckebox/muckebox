import cherrypy

from mutabrainz.autofile import AutoFile
from db.models.album import Album
from db.db import Db

class ArtworkAPI(object):
    @cherrypy.expose
    def default(self, album_id):
        if not (album_id and album_id.isdigit()):
            raise cherrypy.HTTPError(400)

        q = Db.get_session().query(Album).filter(Album.id == int(album_id))

        for album in q:
            ret = AutoFile(album.tracks[0].file.path).get_picture()

            if ret:
                return ret

        raise cherrypy.HTTPError(404)
