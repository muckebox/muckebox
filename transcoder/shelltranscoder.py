import subprocess

from basetranscoder import BaseTranscoder
from abc import abstractmethod

class ShellTranscoder(BaseTranscoder):
    BLOCK_SIZE = 32 * 1024

    def __init__(self, path, queue, quality):
        BaseTranscoder.__init__(self, path, queue, quality)

        self.stop = False

    @abstractmethod
    def get_command(self):
        pass

    def set_source_file(self, path):
        self.path = path

    def run(self):
        self.process = subprocess.Popen(self.get_command(),
                                        stdout = subprocess.PIPE,
                                        bufsize = self.BLOCK_SIZE)
        
        while True:
            block = self.process.stdout.read(self.BLOCK_SIZE)

            if block:
                self.queue.put(block)

            if self.process.poll() is not None:
                if not self.stop:
                    self.set_completed()

                self.queue.put(False)

                break

    def abort(self):
        self.stop = True

        if self.process:
            self.process.terminate()
        
        
