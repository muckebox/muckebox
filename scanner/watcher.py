import pyinotify
import threading

class Watcher(threading.Thread):
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
            self.queue.put(event.pathname)

    def __init__(self, path, queue):
        threading.Thread.__init__(self)
        self.path = path
        self.queue = queue
        self.stop_thread = False

    def run(self):
        wm = pyinotify.WatchManager()

        mask = \
            pyinotify.IN_CLOSE_WRITE | \
            pyinotify.IN_DELETE | \
            pyinotify.IN_MOVED_FROM | \
            pyinotify.IN_MOVED_TO
        
        handler = self.EventHandler(self.queue)
        self.notifier = pyinotify.Notifier(wm, handler)

        wm.add_watch(self.path, mask, rec = True)

        print "Watching %s" % (self.path)

        while not self.stop_thread:
            if self.notifier.check_events(500):
                self.notifier.read_events()
                self.notifier.process_events()

        self.notifier.stop()

        print "WARNING: Watcher for '%s' stopped!" % (self.path)

    def stop(self):
        self.stop_thread = True

