import webapp2
import jinja2
import logging
import os
import webbrowser

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import api
import database
import time

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# @ndb.transactional
def readfromDatabase():
    response_html = jinja_env.get_template('templates/checklist.html')
    user = users.get_current_user()
    logging.info('current user is %s' % (user.nickname()))
    values= {
    "wantsList": database.DatabaseEntry.query(database.DatabaseEntry.type == "want", database.DatabaseEntry.username == user.nickname()).fetch(),
    "needsList": database.DatabaseEntry.query(database.DatabaseEntry.type == "need", database.DatabaseEntry.username == user.nickname()).fetch(),
    "boughtList": database.DatabaseEntry.query(database.DatabaseEntry.type == "bought", database.DatabaseEntry.username == user.nickname()).fetch(),
    'user_nickname': user.nickname(),
    'logoutUrl': users.create_logout_url('/')
    }
    return response_html.render(values)

# @ndb.transactional
def storedStuff(user, typeSelector, item):
    stored_items = database.DatabaseEntry(username=user, type= typeSelector, value= item)
    stored_items.put()

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.headers['Content-Type'] = 'text/html'
        response_html = jinja_env.get_template('templates/index.html')
        if user != None:
            user = users.get_current_user()
            logging.info('current user is %s' % (user.nickname()))
            logout = ''
            if user == '':
                logout = ''
            else:
                logout = 'Log out'
            data = {
            'user_nickname': user.nickname(),
            'logoutUrl': users.create_logout_url('/'),
            'logout': logout
            }
            self.response.write(response_html.render(data))
        else:
            self.response.write(response_html.render())

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),

], debug= True)
