__author__ = 'vadimivlev'

import webapp2

from google.appengine.api import urlfetch


class ListHandler(webapp2.RequestHandler):
    def get(self):
        path=self.request.path_qs.replace("/proxy/","")
        resp=urlfetch.fetch(path)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers=resp.headers.data
        #        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(resp.content)


app = webapp2.WSGIApplication(
    [
        ('/proxy/.*', ListHandler)
    ],  debug=True )

