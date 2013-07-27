import subprocess
import os
import sys
import threading
import signal

import cherrypy

from abc import abstractmethod
from basetranscoder import BaseTranscoder
from utils.threadmanager import ThreadManager

class ShellTranscoder(BaseTranscoder):
    LOG_TAG = "SHELLTRANSCODER"
    BLOCK_SIZE = 32 * 1024

    FNULL = open(os.devnull, 'w')

    lock = threading.Lock()
    paused = False

    def __init__(self, input, queue, output):
        BaseTranscoder.__init__(self, input, queue, output)

        self.stop = False

        self.name = self.LOG_TAG

    @abstractmethod
    def get_command(self):
        pass

    def set_source_file(self, path):
        self.path = path

    def start_process(self):
        self.process = subprocess.Popen(self.get_command(),
                                        stdout = subprocess.PIPE,
                                        stderr = self.FNULL,
                                        bufsize = self.BLOCK_SIZE)

    def stop_process(self):
        if self.process:
            self.process.kill()
        
    def run(self):
        self.start_process()

        bytes_total = 0

        try:
            while True:
                try:
                    ThreadManager.status("READ (%d)" % (bytes_total))

                    block = self.process.stdout.read(self.BLOCK_SIZE)
                
                    self.lock.acquire()

                    try:
                        if block:
                            bytes_total += len(block)

                            ThreadManager.status("PUT (%d)" % (bytes_total))
                        
                            self.queue.put(block)
                        else:
                            ThreadManager.status("WAIT")
                            self.process.wait()

                            if not self.stop:
                                self.set_completed()
                                self.queue.put(None)
                        
                                break
                    finally:
                        self.lock.release()
                except:
                    cherrypy.log.error("Shell transcoding failed!",
                                       self.LOG_TAG)
                    cherrypy.log.error(sys.exc_info()[0], self.LOG_TAG)
                    self.queue.put(None)

                    raise

        finally:
            self.done()
            ThreadManager.status("DONE")

    def abort(self):
        self.stop = True
        self.resume()
        self.stop_process()

    def pause(self):
        if not self.paused:
            self.lock.acquire()
            self.paused = True
            
            if self.process:
                os.kill(self.process.pid, signal.SIGSTOP)

    def resume(self):
        if self.paused:
            self.paused = False
            self.lock.release()

            if self.process:
                os.kill(self.process.pid, signal.SIGCONT)
