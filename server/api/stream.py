import cherrypy
import Queue
import logging

from transcoder import AutoTranscoder, TranscoderManager
from utils import ThreadManager

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

        queue = Queue.Queue()

        output_config = AutoTranscoder.OutputConfiguration(
            path = False,
            format = format,
            quality = self.QUALITY_STRINGS[quality],
            max_bits_per_sample = int(max_bits_per_sample),
            max_sample_rate = int(max_sample_rate),
            offset = 0)

        transcoder = TranscoderManager.get_transcoder(
            int(track_id), output_config, queue)

        if not transcoder:
            raise cherrypy.HTTPError(404)

        cherrypy.response.headers["Content-Type"] = transcoder.get_mime_type()

        return self.stream(transcoder, queue)

    @staticmethod
    def stream(transcoder, queue):
        try:
            while True:
                block = queue.get()
                
                if block is None:
                    transcoder.join()
                    break

                try:
                    yield block
                except GeneratorExit:
                    cherrypy.log('Connection interrupted', LOG_TAG,
                                 logging.WARNING)
                    raise
        finally:
            transcoder.remove_listener(queue)

    default._cp_config = { 'response.stream': True }
