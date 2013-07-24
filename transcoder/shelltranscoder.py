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

    def start_process(self):
        self.process = subprocess.Popen(self.get_command(),
                                        stdout = subprocess.PIPE,
                                        stderr = subprocess.DEVNULL,
                                        bufsize = self.BLOCK_SIZE)

    def stop_process(self):
        if self.process:
            self.process.kill()
        
    def run(self):
        self.start_process()

        bytes_total = 0

        while True:
            block = self.process.stdout.read(self.BLOCK_SIZE)
            retcode = self.subprocess.poll()

            if not block or len(block) == 0 or retcode != None:
                if not self.stop:
                    self.set_completed()

                self.queue.put(False)

                break

            if block:
                bytes_total += len(block)

                self.queue.put(block)

    def abort(self):
        self.stop = True
        self.stop_process()
        
