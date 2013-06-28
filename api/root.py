from artists import ArtistsAPI
from albums import AlbumsAPI
from tracks import TracksAPI

from stream import StreamAPI

from artwork import ArtworkAPI

from ping import PingAPI
from status import StatusAPI

class Root(object):
    class API(object):
        artists = ArtistsAPI()
        albums = AlbumsAPI()
        tracks = TracksAPI()

        stream = StreamAPI()

        artwork = ArtworkAPI()

        ping = PingAPI()
        status = StatusAPI()

    api = API()
