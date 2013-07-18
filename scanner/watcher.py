import pyinotify
import threading
import os.path

from walker import Walker

class Watcher(object):
    class EventHandler(pyinotify.ProcessEvent):
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
            print "Update on %s" % (event.pathname)

            if os.path.isdir(event.pathname):
                Walker(event.pathname, self.queue).start()
            else:
                self.queue.put(event.pathname)

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

        print "Watching %s" % (self.path)

    def stop(self):
        self.notifier.stop()

    def join(self):
        self.notifier.join()

