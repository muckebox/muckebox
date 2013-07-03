import threading
import cherrypy

from root import Root

class API(threading.Thread):
    def __init__(self, port = 2342):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        cherrypy.config.update({
                'server.socket_host': '0.0.0.0',
                'server.socket_port': self.port,
                'tools.gzip.on': True,
                'tools.gzip.mime_types': ['text/*', 'application/json']
                })
        cherrypy.engine.autoreload.unsubscribe()
        cherrypy.quickstart(Root())

    def stop(self):
        cherrypy.engine.exit()
        
