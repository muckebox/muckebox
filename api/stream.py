import cherrypy
import mimetypes

from models.track import Track
from models.file import File
from db import Db

class StreamAPI(object):
    BLOCK_SIZE = 32 * 1024

    @cherrypy.expose
    def default(self, trackid):
        if not (trackid and trackid.isdigit()):
            raise cherrypy.HTTPError(400)

        session = Db().get_session()
        file_name = self.get_file_name(int(trackid), session)

        mime_type, encoding = mimetypes.guess_type(file_name)

        if mime_type:
            cherrypy.response.headers["Content-Type"] = mime_type
        else:
            raise cherrypy.HTTPError(500)

        if encoding:
            cherrypy.response.headers["Content-Encoding"] = encoding

        return self.stream(file_name)

    @staticmethod
    def stream(file_name, block_size = BLOCK_SIZE):
        with open(file_name, "rb") as f:
            while True:
                block = f.read(block_size)

                if not block:
                    break

                yield block

    def get_file_name(self, trackid, session):
        return session.query(File).join(Track).filter(Track.id == trackid).\
            one().path

    default._cp_config = { 'response.stream': True }
