import cherrypy
import json

LOG_TAG = "ERROR"

def handle_error(status, message, traceback, version):
    cherrypy.log("Caught error %s (%s)" % (status, message), LOG_TAG)

    cherrypy.response.headers['Content-Type'] = 'application/json'
    
    return json.dumps({ 'error': True, 'message': message })
    
