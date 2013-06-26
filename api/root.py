from artists import ArtistsAPI
from albums import AlbumsAPI
from tracks import TracksAPI
from stream import StreamAPI

class Root(object):
    class API(object):
        artists = ArtistsAPI()
        albums = AlbumsAPI()
        tracks = TracksAPI()
        stream = StreamAPI()

    api = API()
