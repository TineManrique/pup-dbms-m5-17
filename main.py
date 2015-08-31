import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users
import jinja2
import os
import logging
import json
import urllib


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.
class User(ndb.Model):
    created_by = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True)
    phone_number = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Thesis(ndb.Model):
    created_by = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    year = ndb.IntegerProperty(indexed=True)
    title = ndb.StringProperty(indexed=True)
    abstract = ndb.StringProperty(indexed=True)
    adviser = ndb.StringProperty(indexed=True)
    section = ndb.IntegerProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
  
class RegisterPageHandler(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()
        if loggedin_user: 
            user_key = ndb.Key('User', loggedin_user.user_id())
            user = user_key.get()
            if user:
                url = users.create_logout_url('/home')
                url_linktext = 'LOG OUT'
                status = 'Hello, '
                template_values = {
                    'url': url,
                    'url_linktext': url_linktext,
                    'status' : status
                }
                self.redirect('/home')
            else:
                template = JINJA_ENVIRONMENT.get_template('register.html')
                self.response.write(template.render())
        else:
            self.redirect(users.create_login_url('/register'))

    def post(self):

        user = User(id=users.get_current_user().user_id(), email= users.get_current_user().email(), first_name = self.request.get('first_name'), last_name = self.request.get('last_name'), phone_number = self.request.get('phone_number')) 
        user.put()
        self.redirect('/home')

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
       
        user = users.get_current_user()

        if user:

            url = users.create_logout_url('/login')
            url_linktext = 'LOG OUT'
            status = 'Hello, '
            template_values = {
            'user': user,
            'status': status,
            'url': url,
            'url_linktext': url_linktext,
            }

            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.response.write(template.render(template_values))

        else:
            url = users.create_login_url('/home')
            url_linktext = 'LOG IN'
            status = 'Log in to your account'
            user = ' ' 
            template_values = {
                'user': user,
                'status': status,
                'url': url,
                'url_linktext': url_linktext,
            }
            
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render())
            
    def post(self):
       
        thesis = Thesis()
       
        thesis.created_by = users.get_current_user().user_id()
        thesis.email = users.get_current_user().email()
        thesis.year = int(self.request.get('year'))
        thesis.title = self.request.get('title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.section = int(self.request.get('section'))
        thesis.key = thesis.put()
        thesis.put()
        self.redirect('/')

class APIThesisHandler(webapp2.RequestHandler):
    def get(self):
        thesiss = Thesis.query().order(-Thesis.date).fetch()
        users = User.query().order(-User.date).fetch()
        thesis_list = []
        user_list = []

        for thesis in thesiss:
            created_by = ndb.Key('User', thesis.created_by)
            thesis_list.append({
                'created_by': thesis.created_by,
                'email' : thesis.email,
                'id': thesis.key.id(),
                'year' : thesis.year,
                'title' : thesis.title,
                'abstract' : thesis.abstract,
                'adviser' : thesis.adviser,
                'section' : thesis.section,
                'first_name' : created_by.get().first_name,
                'last_name' : created_by.get().last_name
                });

        response = {
             'result' : 'OK',
             'data' : thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        thesis = Thesis()
        
        thesis.created_by = users.get_current_user().user_id()
        thesis.email = users.get_current_user().email()
        thesis.year = int(self.request.get('year'))
        thesis.title = self.request.get('title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.section = int(self.request.get('section'))
        thesis.key = thesis.put()
        user.key = user.put()
        thesis.put()
        user.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
        'result' : 'OK',
        'data':{
                'created_by': thesis.created_by,
                'email' : thesis.email,              
                'id': thesis.key.id(),
                'year' : thesis.year,
                'title' : thesis.title,
                'abstract' : thesis.abstract,
                'adviser' : thesis.adviser,
                'section' : thesis.section,
                'first_name' : created_by.get().first_name,
                'last_name' : created_by.get().last_name
        }
        }
        self.response.out.write(json.dumps(response))

class APIUserHandler(webapp2.RequestHandler):
    def get(self):
        users = User.query().order(-User.date).fetch()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.key.id(),
                'created_by': user.created_by,
                'email' : user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number':user.phone_number
                });
            
        response = {
             'result' : 'OK',
             'data' : user_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))
        
    def post(self):
        user = User()
       
        user.first_name = self.request.get('first_name')
        user.last_name = self.request.get('last_name')
        user.phone_number = self.request.get('phone_number')
        user.email = users.get_current_user().email()
        user.key = user.put()
        user.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
        'result' : 'OK',
        'data':{
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
        }
        }
        self.response.out.write(json.dumps(response))

class DeleteEntry(webapp2.RequestHandler):
    def get(self, thesis_id):
        thesis = Thesis.get_by_id(int(thesis_id))
        thesis.key.delete()
        self.redirect('/home')

class EditEntry(webapp2.RequestHandler):
    def get(self, thesis_id):
        thesis = Thesis.get_by_id(int(thesis_id))
        template_data = {
            'thesis': thesis
        }
        user = users.get_current_user()

        if user:

            url = users.create_logout_url(self.request.uri)
            url_linktext = 'LOG OUT'
            status = 'Hello, '
            template_values = {
            'user': user,
            'status': status,
            'url': url,
            'url_linktext': url_linktext,
            }
        
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(template_values))
        template = JINJA_ENVIRONMENT.get_template('edit.html')
        self.response.write(template.render(template_data))

    def post(self, thesis_id):
        
        thesis = Thesis.get_by_id(int(thesis_id))
        thesis.created_by = users.get_current_user().user_id()
        thesis.email = users.get_current_user().email()
        thesis.year = int(self.request.get('year'))
        thesis.title = self.request.get('title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.section = int(self.request.get('section'))
        thesis.put()
        self.redirect('/home')

class LoginPageHandler(webapp2.RequestHandler):
    def get(self):
      
        user = users.get_current_user()

        if user:

            url = users.create_logout_url('/login')
            url_linktext = 'LOG OUT'
            status = 'Hello, '

            template_values = {
                'user': user,
                'status': status,
                'url': url,
                'url_linktext': url_linktext,
            }
  
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render())
            
        else:
            url = users.create_login_url('/register')
            url_linktext = 'LOG IN'
            status = 'Log in to your account'
            user = ' ' 
           
            template_values = {
            'user': user,
            'status': status,
            'url': url,
            'url_linktext': url_linktext,
            }

            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render())
          
app = webapp2.WSGIApplication([
    ('/register', RegisterPageHandler),
    ('/login', LoginPageHandler),
    ('/edit_thesis/(.*)', EditEntry),
    ('/delete_thesis/(.*)', DeleteEntry),
    ('/api/thesis', APIThesisHandler),
    ('/api/user', APIUserHandler),
    ('/home', MainPageHandler)
], debug=True)
