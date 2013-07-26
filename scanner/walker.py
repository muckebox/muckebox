import threading
import time
import os

import cherrypy

from pathupdate import PathUpdate

class Walker(threading.Thread):
    LOG_TAG = "WALKER"

    def __init__(self, path, queue, force_update = False):
        threading.Thread.__init__(self)
        self.path = path
        self.queue = queue
        self.force_update = force_update

        self.name = self.LOG_TAG

    def log(self, msg):
        cherrypy.log(msg, self.LOG_TAG)

    def run(self):
        start = time.clock()

        for root, dirs, files in os.walk(self.path.decode("utf-8")):
            for f in files:
                full_path = u"%s/%s" % (root, f)
                self.queue.put(PathUpdate(full_path, self.force_update))
             
        end = time.clock()

        self.log("Traversed %s in %s seconds" % (self.path, end - start))
