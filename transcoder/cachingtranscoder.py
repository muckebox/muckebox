import os
import time
import Queue

import cherrypy

from wrappingtranscoder import WrappingTranscoder
from basetranscoder import BaseTranscoder
from cachemanager import CacheManager

from db.models import Transcoding

from utils import FileLockGuard

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

        with FileLockGuard(self.output_path, 'wb') as self.file_handle:
            while True:
                block = self.slave_queue.get()

                if block is not None:
                    self.file_handle.write(block)

                self.send_to_listeners(block)

                if block is None:
                    break

        self.transcoder.join()

        if self.transcoder.has_completed():
            new_transcoding = Transcoding(
                source_path = self.source_path,
                format = self.get_suffix(),
                quality = self.quality,
                bits_per_sample = self.transcoder.get_output_bits_per_sample(),
                sample_rate = self.transcoder.get_output_sample_rate(),
                path = self.output_path,
                size = os.stat(self.output_path).st_size,
                created = int(time.time()))

            CacheManager.add_transcoding(new_transcoding)
        else:
            os.unlink(self.output_path)

    def flush(self):
        if self.file_handle:
            self.file_handle.flush()

    def get_stream_path(self):
        return self.output_path


