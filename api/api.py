import threading
import logging
import cherrypy
import os.path

from root import Root
from config import Config

class API(threading.Thread):
    LOG_TAG = "API"

    def __init__(self, port = 2342):
        threading.Thread.__init__(self)
        self.port = port

    def configure_server(self, config):
        config.update({
                'server.socket_host': '0.0.0.0',
                'server.socket_port': self.port,
            })

    def configure_app(self, config):
        config.update({
                '/': {
                    'tools.gzip.on': True,
                    'tools.gzip.mime_types': ['text/*', 'application/json'],
                    'tools.encode.on': True
                    }
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
                cherrypy.log("Key file %s missing" % (keyfile), \
                                 self.LOG_TAG, logging.WARNING)
    
            if not os.path.exists(crtfile):
                cherrypy.log("Certificate file %s missing" % (crtfile), \
                                 self.LOG_TAG, logging.WARNING)

            cherrypy.log("SSL disabled", self.LOG_TAG, logging.WARNING)

    def run(self):
        config = { }
        app_config = { }
        
        self.configure_server(config)
        self.configure_ssl(config)
        self.configure_app(app_config)

        cherrypy.config.update(config)
        cherrypy.engine.autoreload.unsubscribe()
        cherrypy.tree.mount(Root(), config = app_config)
        cherrypy.engine.start()

    def stop(self):
        cherrypy.engine.exit()
        
