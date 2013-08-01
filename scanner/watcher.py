import pyinotify
import threading
import time
import os

import cherrypy

from walker import Walker
from pathupdate import PathUpdate
from utils import DelayedTask

class Watcher(object):
    LOG_TAG = "WATCHER"

    class EventHandler(pyinotify.ProcessEvent):
        LOG_TAG = "WATCHEVENTHANDLER"
        UPDATE_DELAY = 2.0

        current_timer = None

        def __init__(self, queue):
            pyinotify.ProcessEvent.__init__(self)
            
            self.queue = queue
            self.delayed_task = DelayedTask(self.UPDATE_DELAY)

        def process_default(self, event):
            path = event.pathname.decode('utf-8')

            def update():
                if os.path.isdir(path):
                    Walker(path, self.queue, False, 1).start()
                else:
                    self.queue.put((1, PathUpdate(path, False)))

            self.delayed_task.post(update, path)

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

