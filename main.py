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

class AboutUsPageHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.headers['Content-Type'] = 'text/html'
        response_html = jinja_env.get_template('templates/aboutus.html')
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
    #def post(self):

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        itemID = self.request.get("item_id")
        user = users.get_current_user()
        logging.info('current user is %s' % (user.nickname()))
        self.response.headers['Content-Type'] = 'text/html'
        response_html = jinja_env.get_template('templates/search.html')
        values = {
        "item_id": itemID,
        "googleApi" : api.googleApi,
        'user_nickname': user.nickname(),
        'logoutUrl': users.create_logout_url('/'),
        }
        self.response.write(response_html.render(values))
    def post(self):
        item = self.request.get('newItem')
        typeSelector = self.request.get('choiceSearch')
        self.response.headers['Content-Type'] = 'text/html'
        print("hello")
        user = users.get_current_user()
        logging.info('current user is %s' % (user.nickname()))
        data = {
          'user_nickname': user.nickname(),
          'logoutUrl': users.create_logout_url('/'),
        }
        storedStuff(user.nickname(), typeSelector, item)
        time.sleep(0.5)
        response_html = jinja_env.get_template('templates/search.html')
        self.response.write(response_html.render(data))

class ChecklistHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(readfromDatabase())

    def post(self):
        user = users.get_current_user()
        item = self.request.get('item')
        typeSelector = self.request.get('choice')
        self.response.headers['Content-Type'] = 'text/html'
        storedStuff(user.nickname(), typeSelector, item)
        time.sleep(0.5)
        self.response.headers['Content-Type'] = 'text/html'
        logging.info('current user is %s' % (user.nickname()))
        response_html = jinja_env.get_template('templates/checklist.html')
        values= {
        "wantsList": database.DatabaseEntry.query(database.DatabaseEntry.type == "want", database.DatabaseEntry.username == user.nickname()).fetch(),
        "needsList": database.DatabaseEntry.query(database.DatabaseEntry.type == "need", database.DatabaseEntry.username == user.nickname()).fetch(),
        "boughtList": database.DatabaseEntry.query(database.DatabaseEntry.type == "bought", database.DatabaseEntry.username == user.nickname()).fetch(),
        'user_nickname': user.nickname(),
        'logoutUrl': users.create_logout_url('/')
        }
        self.response.write(response_html.render(values))


class DeleteItemHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        item_to_delete = self.request.get('item_id')
        response_html = jinja_env.get_template("templates/remove.html")
        key = ndb.Key(urlsafe=item_to_delete)
        the_item = key.get()
        data= {
            "item_id": the_item.key.urlsafe()
        }
        self.response.write(response_html.render(data))
    def post(self):
        key = ndb.Key(urlsafe=self.request.get('item_id'))
        key.delete()
        self.redirect("/checklist")
        item = self.request.get('item')
        typeSelector = self.request.get('choice')
        user = users.get_current_user()
        storedStuff(user.nickname(), typeSelector, item)
        time.sleep(0.5)
        self.response.headers['Content-Type'] = 'text/html'
        response_html = jinja_env.get_template('templates/checklist.html')
        logging.info('current user is %s' % (user.nickname()))
        values= {
        "wantsList": database.DatabaseEntry.query(database.DatabaseEntry.type == "want", database.DatabaseEntry.username == user.nickname()).fetch(),
        "needsList": database.DatabaseEntry.query(database.DatabaseEntry.type == "need", database.DatabaseEntry.username == user.nickname()).fetch(),
        "boughtList": database.DatabaseEntry.query(database.DatabaseEntry.type == "bought", database.DatabaseEntry.username == user.nickname()).fetch(),
        'user_nickname': user.nickname(),
        'logoutUrl': users.create_logout_url('/')
        }
        self.response.write(response_html.render(values))



app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    ('/aboutus', AboutUsPageHandler),
    ('/search', SearchHandler),
    ('/checklist', ChecklistHandler),
    ('/delete', DeleteItemHandler),
], debug= True)
