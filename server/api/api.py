from artists import ArtistsAPI
from albums import AlbumsAPI
from tracks import TracksAPI

from stream import StreamAPI
from hint import HintAPI

from artwork import ArtworkAPI

from ping import PingAPI
from status import StatusAPI

class API(object):
    artists = ArtistsAPI()
    albums = AlbumsAPI()
    tracks = TracksAPI()

    stream = StreamAPI()
    hint = HintAPI()

    artwork = ArtworkAPI()

    ping = PingAPI()
    status = StatusAPI()
