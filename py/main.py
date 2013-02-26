from google.appengine.ext import webapp
from google.appengine.ext import db

from py.pscs_database import fiscal_data, countries, currencies, data_source, commentator_comments


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')
        fiscal_data().put()
        countries().put()
        currencies().put()
        data_source().put()
        commentator_comments().put()



app = webapp.WSGIApplication([('/main', MainHandler)],
                             debug=True)

