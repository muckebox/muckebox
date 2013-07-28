import cherrypy
import Queue
import logging
import sys

from transcoder import AutoTranscoder, TranscoderManager
from utils import ThreadManager

class StreamAPI(object):
    LOG_TAG = 'STREAMAPI'

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
            offset = self.get_range_offset())

        transcoder = TranscoderManager.get_transcoder(
            int(track_id), output_config, queue)

        if not transcoder:
            raise cherrypy.HTTPError(404)

        cherrypy.response.headers["Content-Type"] = transcoder.get_mime_type()

        return self.stream(transcoder, queue)

    def get_range_offset(self):
        header = cherrypy.request.headers.get('Range', 'bytes=0-')
        ranges = cherrypy.lib.httputil.get_ranges(header, sys.maxint)

        if ranges is None:
            return 0

        first_offset = ranges[0][0]

        return first_offset

    def stream(self, transcoder, queue):
        try:
            while True:
                block = queue.get()
                
                if block is None:
                    transcoder.join()
                    break

                try:
                    yield block
                except GeneratorExit:
                    cherrypy.log('Connection interrupted', self.LOG_TAG,
                                 logging.WARNING)
                    raise
        finally:
            transcoder.remove_listener(queue)

    default._cp_config = { 'response.stream': True }
