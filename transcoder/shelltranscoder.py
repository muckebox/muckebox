import subprocess
import os
import sys
import threading
import signal

import cherrypy

from abc import abstractmethod
from basetranscoder import BaseTranscoder
from utils import ThreadManager, LockGuard

class ShellTranscoder(BaseTranscoder):
    LOG_TAG = "SHELLTRANSCODER"

    FNULL = open(os.devnull, 'w')

    def __init__(self, input, output):
        BaseTranscoder.__init__(self, input, output)

        self.stop = False
        self.name = self.LOG_TAG

        self.pause_lock = threading.Lock()
        self.paused = False

        self.process = False

    @abstractmethod
    def get_command(self):
        pass

    def set_source_file(self, path):
        self.path = path

    def start_process(self):
        self.command = self.get_command()
        self.process = subprocess.Popen(self.command,
                                        stdout = subprocess.PIPE,
                                        stderr = self.FNULL,
                                        bufsize = self.BLOCK_SIZE)

    def stop_process(self):
        if self.process:
            self.process.kill()

    def process_block(self):
        try:
            block = self.process.stdout.read(self.BLOCK_SIZE)

            with LockGuard(self.pause_lock) as l:
                if block:
                    self.send_to_listeners(block)
                else:
                    self.process.wait()

                    if self.process.returncode != 0 and \
                            self.process.returncode is not None:
                        cherrypy.log.error(
                            ("Transcoder returned an error (%d), command " +
                             "was '%s'") % (self.process.returncode,
                                            self.command),
                            self.LOG_TAG)

                    if not self.stop:
                        self.set_completed()
                        
                    return False
        except:
            cherrypy.log.error("Shell transcoding failed!", self.LOG_TAG)

            raise

        return True
        
    def run(self):
        self.start_process()

        try:
            while True:
                if not self.process_block():
                    break
        finally:
            self.done()

    def abort(self):
        self.stop = True
        self.resume()
        self.stop_process()

    def pause(self):
        if not self.paused:
            self.pause_lock.acquire()
            self.paused = True
            
            if self.process:
                os.kill(self.process.pid, signal.SIGSTOP)

    def resume(self):
        if self.paused:
            self.paused = False
            self.pause_lock.release()

            if self.process:
                os.kill(self.process.pid, signal.SIGCONT)

    def is_paused(self):
        return self.paused
