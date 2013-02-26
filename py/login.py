import webapp2
from google.appengine.api import users
import os








class LoginPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            self.redirect(self.request.referer)
        else:
            self.redirect(users.create_login_url(self.request.referer))




class LogoutPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            self.redirect(users.create_logout_url(self.request.referer))
        else:
            self.redirect(self.request.referer)




class GetUserNamePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        self.response.headers['Content-Type'] = 'text/plain'
        if user:
            self.response.out.write(user.nickname())





class GetLoginLink(webapp2.RequestHandler):

    def get_login_link(self):
        ver=str(os.environ['CURRENT_VERSION_ID'])[:6]

        if users.get_current_user():
            s="<span id='userName'>%s</span> <a href='/logout'>Logout</a> <span>v %s</span>"  %  (users.get_current_user().nickname(),ver)
        else:
            s="<a href='/login'>Login</a> <span>v %s</span>" % ver

        return s


    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        s=self.get_login_link()
        self.response.out.write(s)


app = webapp2.WSGIApplication([('/login', LoginPage),('/logout', LogoutPage),('/getusername', GetUserNamePage), ('/getloginlink', GetLoginLink)],
    debug=True)
