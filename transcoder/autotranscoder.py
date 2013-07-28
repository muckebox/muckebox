import hashlib
import os.path
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
        cached_path = self.get_cached_transcoding(input, output)

        if cached_path:
            self.transcoder = NullTranscoder(
                input._replace(path = cached_path), output.offset)
        else:
            transcoder_cls = self.get_transcoder(output.format)

            if transcoder_cls:
                cached_output = output._replace(
                    path = self.get_cached_path(input, output))

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

    @classmethod
    def get_cached_transcoding(cls, input, output):
        session = Db.get_session()
        query = session.query(Transcoding). \
            filter(Transcoding.source_path == input.path). \
            filter(Transcoding.format == output.format). \
            filter(Transcoding.quality == output.quality). \
            filter(Transcoding.bits_per_sample <= output.max_bits_per_sample). \
            filter(Transcoding.sample_rate <= output.max_sample_rate)

        for transcoding in query:
            if not cls.validate_cached_path(input.path, transcoding.path):
                session.delete(transcoding)
                session.commit()
            else:
                return transcoding.path

        return False

    @classmethod
    def validate_cached_path(cls, source_path, dest_path):
        if not os.path.exists(dest_path):
            return False

        if os.path.getmtime(dest_path) < os.path.getmtime(source_path):
            return False

        return True

    @classmethod
    def get_cached_path(cls, input, output):
        filekey = "%s:%d" % (input.id, output.quality)
        h = hashlib.sha1(filekey.encode('utf-8')).hexdigest()
        filename = "%s.%s" % (h, output.format)

        return Config.get_cache_path() + "/" + filename

