import pyinotify
import threading
import time
import os

import cherrypy

from walker import Walker
from pathupdate import PathUpdate

class Watcher(object):
    LOG_TAG = "WATCHER"

    class EventHandler(pyinotify.ProcessEvent):
        LOG_TAG = "WATCHEVENTHANDLER"
        UPDATE_DELAY = 2.0

        current_timer = None

        def __init__(self, queue):
            pyinotify.ProcessEvent.__init__(self)
            
            self.queue = queue

        def process_default(self, event):
            path = event.pathname.decode('utf-8')

            if self.is_timer_scheduled(path):
                self.current_timer.cancel()

            self.post_timer(path)

        def post_timer(self, pathname):
            def update():
                if os.path.isdir(pathname):
                    Walker(pathname, self.queue, False, 1).start()
                else:
                    self.queue.put((1, PathUpdate(pathname, False)))

            self.current_timer = threading.Timer(
                self.UPDATE_DELAY, update)
            self.current_timer.ts = time.time()
            self.current_timer.target = pathname

            self.current_timer.start()

        def is_timer_scheduled(self, pathname):
            return self.current_timer is not None and \
                self.current_timer.target == pathname and \
                time.time() - self.current_timer.ts < self.UPDATE_DELAY

    def __init__(self, path, queue):
        self.path = path
        self.queue = queue

    def start(self):
        wm = pyinotify.WatchManager()

        mask = \
            pyinotify.IN_CLOSE_WRITE | \
            pyinotify.IN_DELETE | \
            pyinotify.IN_MOVED_FROM | \
            pyinotify.IN_MOVED_TO | \
            pyinotify.IN_MODIFY | \
            pyinotify.IN_CREATE
        
        handler = self.EventHandler(self.queue)

        self.notifier = pyinotify.ThreadedNotifier(wm, handler)
        self.notifier.start()

        wm.add_watch(self.path, mask, rec = True, auto_add = True)

        cherrypy.log("Watching '%s'" % (self.path), self.LOG_TAG)

    def stop(self):
        self.notifier.stop()

    def join(self):
        self.notifier.join()

