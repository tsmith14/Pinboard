'''
Created on Aug 31, 2012

@author: Tyler Smith
'''
import webapp2
import jinja2
import os
import cgi

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):
  def get(self):      
        template_values = {
                'title': 'Homework 2'
        }
        template = jinja_environment.get_template('form.html')
        self.response.out.write(template.render(template_values))
        
class Submit(webapp2.RequestHandler):
    def get(self):
        template_values = {
                           'title': 'Homework 2',
                           'imageURL' : cgi.escape(self.request.get('imageURL')),
                           'caption' : cgi.escape(self.request.get('caption'))
                           }
        template = jinja_environment.get_template('formSubmit.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/submit',Submit)],
                              debug=True)