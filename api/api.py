import threading
import cherrypy

from root import Root

class API(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        cherrypy.engine.autoreload.unsubscribe()
        cherrypy.quickstart(Root())

    def stop(self):
        cherrypy.engine.exit()
        
