import mimetypes

from basetranscoder import BaseTranscoder

class NullTranscoder(BaseTranscoder):
    BLOCK_SIZE = 32 * 1024

    def __init__(self, input, queue):
        BaseTranscoder.__init__(self, input, queue)

        self.stop = False

    def set_quality(self, quality):
        pass

    def set_source_file(self, path):
        self.path = path

    def get_suffix(self):
        return ''

    def get_mime_type(self):
        return mimetypes.guess_type(self.path)[0]

    def run(self):
        with open(self.path, 'rb') as f:
            while not self.stop:
                block = f.read(self.BLOCK_SIZE)

                if block:
                    self.queue.put(block)
                else:
                    self.queue.put(None)
                    self.set_completed()
                    break

    def abort(self):
        self.stop = True


