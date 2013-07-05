import threading
import cherrypy
import os.path

from root import Root
from config import Config

class API(threading.Thread):
    def __init__(self, port = 2342):
        threading.Thread.__init__(self)
        self.port = port

    def configure_basic(self, config):
        config.update({
                'server.socket_host': '0.0.0.0',
                'server.socket_port': self.port,
                'tools.gzip.on': True,
                'tools.gzip.mime_types': ['text/*', 'application/json'],
                'tools.encode.on': True
            })

    def configure_ssl(self, config):
        keyfile = Config.get_ssl_path("server.key")
        crtfile = Config.get_ssl_path("server.crt")

        if os.path.exists(keyfile) and os.path.exists(crtfile):
            config.update({
                    'server.ssl_module': 'pyopenssl',
                    'server.ssl_certificate': crtfile,
                    'server.ssl_private_key': keyfile
                    })
        else:
            if not os.path.exists(keyfile):
                print "WARNING: key file %s missing" % (keyfile)
    
            if not os.path.exists(crtfile):
                print "WARNING: crt file %s missing" % (crtfile)

            print "WARNING: SSL disabled"

    def run(self):
        config = { }
        
        self.configure_basic(config)
        self.configure_ssl(config)

        cherrypy.config.update(config)
        cherrypy.engine.autoreload.unsubscribe()
        cherrypy.quickstart(Root())

    def stop(self):
        cherrypy.engine.exit()
        
