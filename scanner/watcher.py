import pyinotify
import threading
import os.path

import cherrypy

from walker import Walker
from pathupdate import PathUpdate

class Watcher(object):
    LOG_TAG = "WATCHER"

    class EventHandler(pyinotify.ProcessEvent):
        LOG_TAG = "WATCHEVENTHANDLER"

        def __init__(self, queue):
            pyinotify.ProcessEvent.__init__(self)
            
            self.queue = queue

        def process_IN_CLOSE_WRITE(self, event):
            self.handle_update(event)
                
        def process_IN_DELETE(self, event):
            self.handle_update(event)

        def process_IN_MOVED_FROM(self, event):
            self.handle_update(event)
            
        def process_IN_MOVED_TO(self, event):
            self.handle_update(event)
                    
        def handle_update(self, event):
            cherrypy.log("Update on '%s'" % (event.pathname), self.LOG_TAG)

            if os.path.isdir(event.pathname):
                Walker(event.pathname, self.queue).start()
            else:
                self.queue.put(PathUpdate(event.pathname, False))

    def __init__(self, path, queue):
        self.path = path
        self.queue = queue

    def start(self):
        wm = pyinotify.WatchManager()

        mask = \
            pyinotify.IN_CLOSE_WRITE | \
            pyinotify.IN_DELETE | \
            pyinotify.IN_MOVED_FROM | \
            pyinotify.IN_MOVED_TO
        
        handler = self.EventHandler(self.queue)

        self.notifier = pyinotify.ThreadedNotifier(wm, handler)
        self.notifier.start()

        wm.add_watch(self.path, mask, rec = True)

        cherrypy.log("Watching '%s'" % (self.path), self.LOG_TAG)

    def stop(self):
        self.notifier.stop()

    def join(self):
        self.notifier.join()

