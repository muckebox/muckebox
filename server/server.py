import threading
import logging
import cherrypy
import os.path

from api import API
from utils import Settings

class Server(threading.Thread):
    LOG_TAG = "SERVER"

    def __init__(self):
        threading.Thread.__init__(self)

    def configure_server(self, config):
        config.update({
                'server.socket_host': '0.0.0.0',
                'server.socket_port': Settings.get_port()
            })

    def configure_ssl(self, config):
        keyfile = Settings.get_ssl_key_path()
        crtfile = Settings.get_ssl_cert_path()

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

    def configure_authentication(self, config):
        password = Settings.get_password()

        if password:
            passdict = { 'muckebox' : password }
            checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(passdict)
            config.update({
                    'tools.auth_basic.on': True,
                    'tools.auth_basic.realm': 'muckebox',
                    'tools.auth_basic.checkpassword': checkpassword
                    })

    def configure_logs(self, config):
        if not Settings.is_foreground():
            config.update({
                    'log.screen': False,
                    'log.access_file': Settings.get_access_log_path(),
                    'log.error_file': Settings.get_error_log_path()
                    })

    def configure(self):
        config = { }

        self.configure_logs(config)
        self.configure_server(config)
        self.configure_ssl(config)
        self.configure_authentication(config)

        cherrypy.config.update(config)

    def run(self):
        self.mount_api()

        cherrypy.engine.autoreload.unsubscribe()
        cherrypy.engine.start()

    def mount_api(self):
        config = { '/': {
                'tools.gzip.on': True,
                'tools.gzip.mime_types': ['text/*', 'application/json'],
                'tools.encode.on': True
                } }

        cherrypy.tree.mount(API(), '/api', config = config)

    def stop(self):
        cherrypy.engine.exit()
        
