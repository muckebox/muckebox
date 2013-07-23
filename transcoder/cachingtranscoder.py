import os
import Queue

from basetranscoder import BaseTranscoder

from db import Db
from models.transcoding import Transcoding

# Wraps another transcoder and adds writing output to a cache

class CachingTranscoder(BaseTranscoder):
    def __init__(self, wrapped_transcoder, source_path, output_path):
        self.transcoder = wrapped_transcoder
        self.source_path = source_path
        self.output_path = output_path
        self.slave_queue = Queue.Queue()

        BaseTranscoder.__init__(self, False, self.transcoder.queue)

        self.transcoder.set_output_queue(self.slave_queue)

    def set_quality(self, quality):
        self.quality = quality
        self.transcoder.set_quality(quality)

    def set_source_file(self, source_path):
        self.source_path = source_path
        self.transcoder.set_source_file(source_file)

    def get_suffix(self):
        return self.transcoder.get_suffix()

    def get_mime_type(self):
        return self.transcoder.get_mime_type()

    def run(self):
        self.transcoder.start()

        with open(self.output_path, 'wb') as f:
            while not self.transcoder.has_finished():
                block = self.slave_queue.get()

                self.queue.put(block)

                if block:
                    f.write(block)
                else:
                    break

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

    def abort(self):
        self.transcoder.abort()
