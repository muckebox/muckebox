import sys

import cherrypy

from transcoder import AutoTranscoder, TranscoderManager

class TranscoderHelper(object):
    QUALITY_STRINGS = {
        'lowest':       AutoTranscoder.Quality.LOWEST,
        'low':          AutoTranscoder.Quality.LOW,
        'medium':       AutoTranscoder.Quality.MEDIUM,
        'high':         AutoTranscoder.Quality.HIGH,
        'highest':      AutoTranscoder.Quality.HIGHEST,
        }
    
    @classmethod
    def get_transcoder_request(cls, track_id, format, quality,
                               max_bits_per_sample, max_sample_rate):
        if not (track_id and track_id.isdigit()):
            raise cherrypy.HTTPError(400)

        if quality not in cls.QUALITY_STRINGS:
            raise cherrypy.HTTPError(400)

        if not str(max_bits_per_sample).isdigit():
            raise cherrypy.HTTPError(400)

        if not str(max_sample_rate).isdigit():
            raise cherrypy.HTTPError(400)

        output_config = AutoTranscoder.OutputConfiguration(
            path = False,
            format = format,
            quality = cls.QUALITY_STRINGS[quality],
            max_bits_per_sample = int(max_bits_per_sample),
            max_sample_rate = int(max_sample_rate),
            offset = cls.get_range_offset())

        return TranscoderManager.Request(
            track_id = int(track_id),
            config = output_config)

    @classmethod
    def get_range_offset(cls):
        header = cherrypy.request.headers.get('Range', 'bytes=0-')
        ranges = cherrypy.lib.httputil.get_ranges(header, sys.maxint)

        if ranges is None:
            return 0

        first_offset = ranges[0][0]

        return first_offset

