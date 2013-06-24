import threading
import time
import os

class Walker(threading.Thread):
    def __init__(self, path, queue):
        threading.Thread.__init__(self)
        self.path = path
        self.queue = queue

    def run(self):
        start = time.clock()

        for root, dirs, files in os.walk(unicode(self.path)):
            for f in files:
                full_path = u"%s/%s" % (root, f)
                self.queue.put(full_path)
             
        end = time.clock()

        print "Traversed %s in %s seconds" % (self.path, end - start)
