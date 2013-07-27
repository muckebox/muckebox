import cherrypy
import Queue
import logging

from transcoder.autotranscoder import AutoTranscoder
from utils.threadmanager import ThreadManager
from db.models.track import Track
from db.db import Db

LOG_TAG = 'STREAMAPI'

class StreamAPI(object):
    BLOCK_SIZE = 32 * 1024

    QUALITY_STRINGS = {
        'lowest':       AutoTranscoder.Quality.LOWEST,
        'low':          AutoTranscoder.Quality.LOW,
        'medium':       AutoTranscoder.Quality.MEDIUM,
        'high':         AutoTranscoder.Quality.HIGH,
        'highest':      AutoTranscoder.Quality.HIGHEST,
        }

    @cherrypy.expose
    def default(self, track_id, format = False, quality = 'high',
                max_bits_per_sample = 16, max_sample_rate = 48000):
        if not (track_id and track_id.isdigit()):
            raise cherrypy.HTTPError(400)

        if quality not in self.QUALITY_STRINGS:
            raise cherrypy.HTTPError(400)

        if not str(max_bits_per_sample).isdigit():
            raise cherrypy.HTTPError(400)

        if not str(max_sample_rate).isdigit():
            raise cherrypy.HTTPError(400)

        ThreadManager.name(LOG_TAG)
        ThreadManager.status("Stream setup")

        session = Db.get_session()
        track = self.get_track(int(track_id), session)

        queue = Queue.Queue()

        input_config = AutoTranscoder.InputConfiguration(
            id = track.stringid,
            track_id = track_id,
            path = track.file.path,
            bits_per_sample = track.bits_per_sample,
            sample_rate = track.sample_rate
            )

        output_config = AutoTranscoder.OutputConfiguration(
            path = False,
            format = format,
            quality = self.QUALITY_STRINGS[quality],
            max_bits_per_sample = max_bits_per_sample,
            max_sample_rate = max_sample_rate)

        transcoder = AutoTranscoder(input_config, queue, output_config)

        cherrypy.response.headers["Content-Type"] = transcoder.get_mime_type()

        transcoder.start()

        return self.stream(transcoder, queue)

    @staticmethod
    def stream(transcoder, queue):
        while True:
            ThreadManager.status("queue.get()")
            block = queue.get()

            if block is None:
                transcoder.join()
                break

            try:
                ThreadManager.status("yield")
                yield block
            except GeneratorExit:
                cherrypy.log('Connection interrupted, stopping transcoding',
                             LOG_TAG, logging.WARNING)
                transcoder.abort()
                raise

        ThreadManager.status("done")

    @staticmethod
    def get_track(trackid, session):
        return session.query(Track).filter(Track.id == trackid).one()

    default._cp_config = { 'response.stream': True }
