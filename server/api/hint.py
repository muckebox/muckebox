import cherrypy

from transcoder import TranscoderManager
from transcoderhelper import TranscoderHelper

class HintAPI(object):
    LOG_TAG = 'HINTAPI'

    @cherrypy.expose
    def default(self, track_id, format = False, quality = 'high',
                max_bits_per_sample = 16, max_sample_rate = 48000):
        request = TranscoderHelper.get_transcoder_request(
            track_id, format, quality, max_bits_per_sample, max_sample_rate)

        TranscoderManager.enqueue_request(request)
