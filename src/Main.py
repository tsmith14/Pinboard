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
        private = db.BooleanProperty()
        owner = db.StringProperty()
        
        def setPrivateStatus(self,value):
            if value == "0":
                self.private = False
            else:
                self.private = True
        
        def getBoards(self,user):
            if (self.owner == user.user_id()):
                return Board.gql("WHERE pins = :1 AND owner = :2 ", self.key(),user.user_id())
            else:
                return Board.gql("WHERE pins = :1 AND private = :2 ", self.key(),False)
#            return Board.gql("WHERE pins = :1 AND owner = :2", self.key(),user.user_id())

        
        def removeFromBoards(self):
            for board in Board.all():
                if board.hasPin(self.key()):
                    board.pins.remove(self.key())
                    board.put()

class Board(db.Model):
        name = db.StringProperty()
        private = db.BooleanProperty()
        pins = db.ListProperty(db.Key)
        date = db.DateTimeProperty(auto_now_add=True)
        owner = db.StringProperty()
        
        def setPrivateStatus(self,value):
            if value == "0":
                self.private = False;
            else:
                self.private = True;
            
        def getPins(self):
            return Pin.get(self.pins)
        
        def hasPin(self,pinKey):
            if pinKey in self.pins:
                return True
            else:
                return False
#            for pin in self.pins:
#                if pin==pinKey:
#                    return True
#            return False
        
        
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
        
    def publicBoards(self):
        boards = Board.all()
        boards.filter("owner !=", self.user.user_id())
        boards.filter("private =",False)
        return boards
    
    def publicPins(self):
        pins = Pin.all()
        pins.filter("owner !=", self.user.user_id())
        pins.filter("private =",False)
        return pins
          
    
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
        self.templateValues['publicPins']  = self.publicPins()
        self.setTemplate("pinIndex.html")
    
    def post(self):
        self.defineUser()
        pin = Pin(imgUrl = self.request.get("imageUrl"), caption =  self.request.get("caption"), owner = self.user.user_id())
        pin.setPrivateStatus(self.request.get("private"))
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
            self.templateValues['boards'] = self.pin.getBoards(self.user)
            if self.pin.owner == self.user.user_id():
                self.templateValues['isEditable'] = True
            else:
                self.templateValues['isEditable'] = False
        self.setTemplate("pinDetails.html")  
    
    def post(self, pinID):
        self.defineUser()
        self.key = db.Key.from_path('Pin', long(pinID))
        self.pin = db.get(self.key)
        if self.pin.owner !=  self.user.user_id():
            self.redirect("/pin")
            return
        if self.request.get("method") == "Delete":
            self.pin.removeFromBoards()
            db.delete(self.key)
            self.redirect("/pin")
            return
        else:
            self.pin.imgUrl = self.request.get("imageUrl")
            self.pin.caption =  self.request.get("caption")
            self.pin.setPrivateStatus(self.request.get("private"))
            self.pin.put()
            self.redirect("/pin/"+str(self.pin.key().id()))
            return
        
class BoardIndex(Universal):
    def get(self):
        self.templateValues = {'title': 'My Boards'}
        self.basicSetup()
        self.checkLogin()
        if not self.loggedIn:
            return
        boards = Board.all()
        boards.filter("owner =", self.user.user_id())
        self.templateValues['boards'] = boards
        self.templateValues['publicBoards']  = self.publicBoards()
        self.setTemplate("boardIndex.html")
    
    def post(self):
        self.defineUser()
        board = Board(name = self.request.get("name"), owner = self.user.user_id())
        board.setPrivateStatus(self.request.get("private"))
        board.put()
        self.redirect("/board/"+str(board.key().id()))
        return
    
           
class BoardDetails(Universal):          
    def get(self, boardID):
        self.templateValues = {'title': 'Board'}
        self.templateValues['boardID'] = boardID
        self.basicSetup()
        self.checkLogin()
        if not self.loggedIn:
            return
        self.key = db.Key.from_path('Board', long(boardID))
        self.board = db.get(self.key)
        if self.board == None:
            self.templateValues['notFound'] = True
            self.templateValues['title'] = "Error"
        else:
            self.templateValues['notFound'] = False
            self.templateValues['title'] = self.board.name;
            self.templateValues['board'] = self.board
            if self.board.owner == self.user.user_id():
                self.templateValues['isEditable'] = True
            else:
                self.templateValues['isEditable'] = False
            pins = Pin.all();
            pins.filter("owner =", self.user.user_id())
            self.templateValues['userPins'] = pins;
            

        self.setTemplate("boardDetails.html")  
    
    def post(self, boardID):
        self.defineUser()
        self.key = db.Key.from_path('Board', long(boardID))
        self.board = db.get(self.key)
        if self.board.owner !=  self.user.user_id():
            self.redirect("/board")
            return
        if self.request.get("method") == "Delete":
            db.delete(self.key)
            self.redirect("/board")
            return
        elif self.request.get("method") == "Add":
            pins = self.request.get_all("pins")
            for pinID in pins:
                key = db.Key.from_path('Pin', long(pinID))
                self.board.pins.append(key);
            self.board.put()
            self.redirect("/board/"+str(self.board.key().id()))
            return
        elif self.request.get("method") == "RemovePin":
            key = db.Key.from_path('Pin', long(self.request.get("pinID")))
            self.board.pins.remove(key)
            self.board.put();
            self.redirect("/board/"+str(self.board.key().id()))
            return
        else:
            self.board.name = self.request.get("name")
            self.board.setPrivateStatus(self.request.get("private"))
            self.board.put()
            self.redirect("/board/"+str(self.board.key().id()))
            return
                
app = webapp2.WSGIApplication([('/', HomePage),
                               ('/pin', PinIndex),('/pin/(.*)', PinDetails),('/board', BoardIndex),('/board/(.*)', BoardDetails)],  #\d+)
                              debug=True)