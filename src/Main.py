'''
Created on Aug 31, 2012

@author: Tyler Smith
'''
import webapp2
import jinja2
import os
import cgi
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):
  def get(self):  
        user = users.get_current_user()
        templateValues = {
                'title': 'Pinboard'
        }
        template = jinja_environment.get_template('master.html')

        if user:
            templateValues["email"] = user.email()
            templateValues["logoutUrl"] = users.create_logout_url(self.request.uri)   
            if self.request.get('imageUrl') != None:
                templateValues['imageUrl'] = self.request.get('imageUrl')
            if self.request.get('caption') != None:
                templateValues['caption'] = self.request.get('caption')
            template = jinja_environment.get_template('form.html')
            
        else:
            templateValues["loginUrl"] = users.create_login_url(self.request.uri)   
            template = jinja_environment.get_template('login.html')
        
        self.response.out.write(template.render(templateValues))
        

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)