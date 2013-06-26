import cherrypy

class PingAPI(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def default(self):
        return { 'pong': True }
