import os
import Queue
import hashlib

import cherrypy

from wrappingtranscoder import WrappingTranscoder
from basetranscoder import BaseTranscoder

from db import Db
from db.models import Transcoding
from utils import ThreadManager, Config

class CachingTranscoder(WrappingTranscoder):
    LOG_TAG = "CACHINGTRANSCODER"

    def __init__(self, wrapped_transcoder, source_path, output_path):
        self.transcoder = wrapped_transcoder
        self.source_path = source_path
        self.output_path = output_path

        self.slave_queue = Queue.Queue()

        WrappingTranscoder.__init__(self, False)

        self.transcoder.add_listener(self.slave_queue)

        self.name = self.LOG_TAG

    def get_stream_path(self):
        return self.output_path

    def set_quality(self, quality):
        self.quality = quality
        self.transcoder.set_quality(quality)

    def set_source_file(self, source_path):
        self.source_path = source_path
        self.transcoder.set_source_file(source_file)

    def run(self):
        self.transcoder.start()

        with open(self.output_path, 'wb') as self.file_handle:
            while True:
                block = self.slave_queue.get()

                if block is not None:
                    self.file_handle.write(block)

                self.send_to_listeners(block)

                if block is None:
                    break

        self.transcoder.join()

        if self.transcoder.has_completed():
            session = Db.get_session()

            new_transcoding = Transcoding(
                source_path = self.source_path,
                format = self.get_suffix(),
                quality = self.quality,
                bits_per_sample = self.transcoder.get_output_bits_per_sample(),
                sample_rate = self.transcoder.get_output_sample_rate(),
                path = self.output_path)

            session.add(new_transcoding)

            session.commit()
        else:
            os.unlink(self.output_path)

    def flush(self):
        if self.file_handle:
            self.file_handle.flush()

    def get_stream_path(self):
        return self.output_path

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

