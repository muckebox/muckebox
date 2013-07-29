import Queue
import logging

import cherrypy

from transcoder import TranscoderManager
from transcoderhelper import TranscoderHelper

class StreamAPI(object):
    LOG_TAG = 'STREAMAPI'

    @cherrypy.expose
    def default(self, track_id, format = False, quality = 'high',
                max_bits_per_sample = 16, max_sample_rate = 48000):
        request = TranscoderHelper.get_transcoder_request(
            track_id, format, quality, max_bits_per_sample, max_sample_rate)
        queue = Queue.Queue()
        transcoder = TranscoderManager.get_transcoder(request, queue)

        if not transcoder:
            raise cherrypy.HTTPError(404)

        cherrypy.response.headers["Content-Type"] = transcoder.get_mime_type()

        return self.stream(transcoder, queue)

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
