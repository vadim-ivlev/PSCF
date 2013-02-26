from google.appengine.ext import webapp
from google.appengine.api import memcache




class MainHandler(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        if memcache.flush_all():
            self.response.out.write( "flushed" )
        else:
            self.response.out.write( "not flushed" )


app = webapp.WSGIApplication([('/flush_memcache', MainHandler)],
                             debug=True)

