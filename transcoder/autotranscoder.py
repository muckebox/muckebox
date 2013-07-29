import logging

import cherrypy

from cachingtranscoder import CachingTranscoder
from wrappingtranscoder import WrappingTranscoder

from oggtranscoder import OggTranscoder
from mp3transcoder import MP3Transcoder
from opustranscoder import OpusTranscoder
from nulltranscoder import NullTranscoder

from db.models import Transcoding
from db import Db
from utils import Config

class AutoTranscoder(WrappingTranscoder):
    LOG_TAG = "AUTOTRANSCODER"

    TRANSCODER_MAP = {
        'mp3': MP3Transcoder,
        'ogg': OggTranscoder,
        'opus': OpusTranscoder
        }

    def __init__(self, input, output):
        cached_path = CachingTranscoder.get_cached_transcoding(input, output)

        if cached_path:
            self.transcoder = NullTranscoder(
                input._replace(path = cached_path), output.offset)
        else:
            transcoder_cls = self.get_transcoder(output.format)

            if transcoder_cls:
                cached_output = output._replace(
                    path = CachingTranscoder.get_cached_path(input, output))

                transcoder = transcoder_cls(input, cached_output)
                self.transcoder = CachingTranscoder(transcoder,
                                                    input.path,
                                                    cached_output.path)
            else:
                cherrypy.log("Could not find matching transcoder for '%s'" % \
                                 (output.format),
                             self.LOG_TAG, logging.WARNING)
                self.transcoder = NullTranscoder(input, output.offset)

        WrappingTranscoder.__init__(self, input, output)

    def set_source_file(self, path):
        pass

    def add_listener(self, listener):
        self.transcoder.add_listener(listener)
        
    def remove_listener(self, listener):
        self.transcoder.remove_listener(listener)

    def has_listeners(self):
        return self.transcoder.has_listeners()

    def run(self):
        self.transcoder.start()
        self.transcoder.join()

    @classmethod
    def get_transcoder(cls, format):
        if format in cls.TRANSCODER_MAP:
            return cls.TRANSCODER_MAP[format]

        return False


