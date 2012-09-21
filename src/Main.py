'''
Created on Aug 31, 2012

@author: Tyler Smith
'''
import webapp2
import jinja2
import os
from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

def datetimeformat(value, datetimeformat='%B, %d %I:%M%p'):
    return value.strftime(datetimeformat)

jinja_environment.filters['datetimeformat'] = datetimeformat


class Pin(db.Model):
        imgUrl = db.StringProperty()
        caption = db.StringProperty(multiline=True)
        date = db.DateTimeProperty(auto_now_add=True)
        owner = db.StringProperty()
        
class Universal(webapp2.RequestHandler):
    def defineUser(self):
        self.user = users.get_current_user()
        
    def basicSetup(self):
        self.defineUser()
        if self.user:
            self.templateValues["email"] = self.user.nickname()
            self.templateValues["logoutUrl"] = users.create_logout_url(self.request.uri)     
        else:
            self.templateValues["loginUrl"] = users.create_login_url(self.request.uri)
        
    def checkLogin(self):
        self.defineUser()
        self.loggedIn = True
        if not self.user:
            self.redirect("/")
            self.loggedIn = False

            
            
    def setTemplate(self, templateName):
        template = jinja_environment.get_template(templateName)
        self.response.out.write(template.render(self.templateValues))
          
    
class HomePage(Universal):
    def get(self):  
        self.templateValues = {'title': 'Pinboard'}
        self.basicSetup()
        if self.user:
            self.setTemplate("form.html")
        else:
            self.setTemplate("login.html")
#        if self.request.get('imageUrl') != None:
#            self.templateValues['imageUrl'] = self.request.get('imageUrl')
#        if self.request.get('caption') != None:
#            self.templateValues['caption'] = self.request.get('caption')
#            template = jinja_environment.get_template('form.html')
#            template = jinja_environment.get_template('login.html')
        
class PinIndex(Universal):    
    def get(self):
        self.templateValues = {'title': 'My Pins'}
        self.basicSetup()
        self.checkLogin()
        if not self.loggedIn:
            return
        pins = Pin.all()
        pins.filter("owner =", self.user.user_id())
        self.templateValues['pins'] = pins
        self.setTemplate("pinIndex.html")
    
    def post(self):
        self.defineUser()
        pin = Pin(imgUrl = self.request.get("imageUrl"), caption =  self.request.get("caption"), owner = self.user.user_id())
        pin.put()
        self.redirect("/pin/"+str(pin.key().id()))
        return
           
class PinDetails(Universal):          
    def get(self, pinID):
        self.templateValues = {'title': 'My Pin'}
        self.templateValues['pinID'] = pinID
        self.basicSetup()
        self.checkLogin()
        if not self.loggedIn:
            return
        self.key = db.Key.from_path('Pin', long(pinID))
        self.pin = db.get(self.key)
        if self.pin == None:
            self.templateValues['notFound'] = True
            self.templateValues['title'] = "Error"
        else:
            self.templateValues['notFound'] = False
            self.templateValues['title'] = "Pin " + pinID;
            self.templateValues['pin'] = self.pin
        self.setTemplate("pinDetails.html")  
    
    def post(self, pinID):
        self.defineUser()
        self.key = db.Key.from_path('Pin', long(pinID))
        if self.request.get("method") == "Delete":
            db.delete(self.key)
            self.redirect("/pin")
            return
        else:
            self.pin = db.get(self.key)
            self.pin.imgUrl = self.request.get("imageUrl")
            self.pin.caption =  self.request.get("caption")
            self.pin.put()
            self.redirect("/pin/"+str(self.pin.key().id()))
            return
                
app = webapp2.WSGIApplication([('/', HomePage),
                               ('/pin', PinIndex),('/pin/(.*)', PinDetails)],  #\d+)
                              debug=True)