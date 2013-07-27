import mimetypes
import threading

from basetranscoder import BaseTranscoder
from utils import LockGuard

class NullTranscoder(BaseTranscoder):
    pause_lock = threading.Lock()
    paused = False

    def __init__(self, input):
        BaseTranscoder.__init__(self, input)

        self.stop = False

    def set_quality(self, quality):
        pass

    def set_source_file(self, path):
        self.path = path

    def get_stream_path(self):
        return self.path

    def get_suffix(self):
        return ''

    def get_mime_type(self):
        return mimetypes.guess_type(self.path)[0]

    def run(self):
        try:
            with open(self.path, 'rb') as self.file_handle:
                while not self.stop:
                    block = self.file_handle.read(self.BLOCK_SIZE)

                    with LockGuard(self.pause_lock) as l:
                        if block:
                            self.send_to_listeners(block)
                        else:
                            self.set_completed()
                            break
        finally:
            self.done()

    def abort(self):
        self.stop = True
        self.resume()

    def pause(self):
        if not self.paused:
            self.pause_lock.acquire()
            self.paused = True
        
    def resume(self):
        if self.paused:
            self.paused = False
            self.pause_lock.release()

    def is_paused(self):
        return self.paused

    def flush(self):
        if self.file_handle:
            self.file_handle.flush()
