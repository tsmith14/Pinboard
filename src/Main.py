'''
Created on Aug 31, 2012

@author: Tyler Smith
'''
import webapp2
import jinja2
import os
import json
import logging
from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

def datetimeformat(value, datetimeformat='%B, %d %I:%M%p'):
    return value.strftime(datetimeformat)

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

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

        
        def removeFromBoards(self):
            for board in Board.all():
                if board.hasPin(self.key()):
                    board.pins.remove(self.key())
                    board.put()

class Board(db.Model):
        name = db.StringProperty()
        private = db.BooleanProperty()
        pins = db.ListProperty(db.Key)
        locations = db.StringListProperty()
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
        
        def addLocation(self,pinID,x,y):
            locationArray = {"id":long(pinID),"x": long(x),"y":long(y)}
            self.locations.append(json.dumps(locationArray))
            self.put()
            
            
        def removeLocation(self,pinID):
            for location in self.locations:
                locationArray = json.loads(location)
                if long(locationArray['id']) == pinID:
                    self.locations.remove(location)
                    self.put()
                    return  
       
        def getPinXLocation(self,pinID):   
            for location in self.locations:
                locationArray = json.loads(location)
                if long(locationArray['id']) == pinID:
                    return locationArray['x'];
            return 0;   
        
        def getPinYLocation(self,pinID):   
            for location in self.locations:
                locationArray = json.loads(location)
                if long(locationArray['id']) == pinID:
                    return locationArray['y'];
            return 0;    
        
        def updatePinLocation(self,pinID,x,y):
            for location in self.locations:
                locationArray = json.loads(location)
                if long(locationArray['id']) == long(pinID):
                    logging.info("HERE2")
                    self.locations.remove(location)
                    self.locations.append(json.dumps({"id":pinID,"x":x,"y":y}))                   
                    return
        
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
            self.loggedIn = False
    
    def redirectToHome(self):
        self.redirect("/")
            
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
    
    
    def generateNotFoundError(self):
        self.error(404)
        self.response.out.write("<html><h1>404 Not Found</h1>The resource could not be found.</html>")
    
    def findExtension(self,value):
        components = value.split(".")
        self.ID = components[0]
        self.extension = None
        self.isError = False
        if len(components) == 2:
            self.extension = components[1]
        elif len(components) > 2:
            self.isError = True
            return

          
    
class HomePage(Universal):
    def get(self):  
        self.templateValues = {'title': 'Pinboard'}
        self.basicSetup()
        if self.user:
            self.setTemplate("home.html")
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
        self.findExtension(self.request.path)
        self.checkLogin()
        pins = Pin.all()
        if self.user:
            pins.filter("owner =", self.user.user_id())
        if self.request.get("fmt") == "json" or self.extension == "json":
            if not self.loggedIn:
                self.error(401)  
                return;
            self.jsonDictionary = []
            for pin in pins:
                self.jsonDictionary.append(db.to_dict(pin))
            self.response.headers["Content-Type"] = "application/json"
            self.response.out.write(json.dumps(self.jsonDictionary, default=date_handler))
        else:   
            if not self.extension == None:
                self.generateNotFoundError();
                return
            self.templateValues = {'title': 'Pins'}
            self.basicSetup()
            if not self.loggedIn:
                self.redirectToHome()
                return
            pins = Pin.all()
            pins.filter("owner =", self.user.user_id())
            self.templateValues['pins'] = pins
            self.templateValues['publicPins']  = self.publicPins()
            self.setTemplate("pinIndex.html")
    
    def post(self):
        self.checkLogin()
        if not self.loggedIn:
            self.redirectToHome()
            return
        pin = Pin(imgUrl = self.request.get("imageUrl"), caption =  self.request.get("caption"), owner = self.user.user_id())
        pin.setPrivateStatus(self.request.get("private"))
        pin.put()
        self.redirect("/pin/"+str(pin.key().id()))
        return
           
class PinDetails(Universal):          
    def get(self, urlValue):
        self.findExtension(urlValue)
        if self.isError:
            self.generateNotFoundError()
            return
        self.checkLogin()
        self.key = db.Key.from_path('Pin', long(self.ID))
        self.pin = db.get(self.key)
        if self.request.get("fmt") == "json" or self.extension == "json":
            if not self.loggedIn:
                self.error(401)  
                return;
            self.jsonDictionary = [db.to_dict(self.pin)]
            self.response.headers["Content-Type"] = "application/json"
            self.response.out.write(json.dumps(self.jsonDictionary, default=date_handler))
            return
        elif self.extension == None:
            if not self.loggedIn:
                self.redirectToHome()
                return
            self.templateValues = {'title': 'My Pin'}
            self.templateValues['pinID'] = self.ID
            self.basicSetup()

            if self.pin == None:
                self.templateValues['notFound'] = True
                self.templateValues['title'] = "Error"
            else:
                self.templateValues['notFound'] = False
                self.templateValues['title'] = "Pin " + self.ID;
                self.templateValues['pin'] = self.pin
                self.templateValues['boards'] = self.pin.getBoards(self.user)
                if self.pin.owner == self.user.user_id():
                    self.templateValues['isEditable'] = True
                else:
                    self.templateValues['isEditable'] = False
            self.setTemplate("pinDetails.html")  
        else:
            self.generateNotFoundError()
            return
    
    def post(self, pinID):
        self.checkLogin()
        if not self.loggedIn:
            self.redirectToHome()
            return
        self.key = db.Key.from_path('Pin', long(pinID))
        self.pin = db.get(self.key)
        if self.pin.owner !=  self.user.user_id():
            self.response.out.write("Sorry, you do not have rights to edit this pin");
            return
        if self.request.get("method") == "Delete":
            self.pin.removeFromBoards()
            db.delete(self.key)
            self.redirect("/pin")
            return
        elif self.request.get("private"):
            self.pin.setPrivateStatus(self.request.get("private"))
            self.pin.put();
            if (self.pin.private):
                self.response.out.write("Pin is private")
            else:
                self.response.out.write( "Pin is public")
            return
        elif self.request.get("caption"):
            self.pin.caption = self.request.get("caption")
            self.pin.put();
            self.response.out.write(self.pin.caption)
            return
        else:
            self.response.out.write("ERROR")
            return

        
class BoardIndex(Universal):
    def get(self):
        self.templateValues = {'title': 'Boards'}
        self.basicSetup()
        self.checkLogin()
        if not self.loggedIn:
            self.redirectToHome()
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
    def get(self, urlValue):
        self.findExtension(urlValue)
        if self.isError:
            self.generateNotFoundError()
            return
        self.checkLogin()
        self.key = db.Key.from_path('Board', long(self.ID))
        self.board = db.get(self.key)
        if self.request.get("fmt") == "json" or self.extension == "json":
            if not self.loggedIn and self.board.private:
                self.error(401)  
                return;
            self.jsonDictionary = db.to_dict(self.board)
            self.jsonDictionary['pins'] = [];
            self.boardPinArray = []
            for pin in self.board.getPins():
                    pinDict = db.to_dict(pin)
                    pinDict["id"] = pin.key().id()
                    pinDict["x"] = self.board.getPinXLocation(pin.key().id())
                    pinDict["y"] = self.board.getPinYLocation(pin.key().id())
                    self.boardPinArray.append(pinDict)
            self.jsonDictionary['pins'] = self.boardPinArray
            self.allPins = [];
            if self.user:
                for pin in Pin.all().filter("owner =", self.user.user_id()):
                    try:
                        pinDict = db.to_dict(pin)
                        pinDict["id"] = pin.key().id()
                        pinDict["x"] = self.board.getPinXLocation(pin.key().id())
                        pinDict["y"] = self.board.getPinYLocation(pin.key().id())
                        self.boardPinArray.index(pinDict)
                    except Exception:
                        pinDict = db.to_dict(pin)
                        pinDict["id"] = pin.key().id()
                        pinDict["x"] = self.board.getPinXLocation(pin.key().id())
                        pinDict["y"] = self.board.getPinYLocation(pin.key().id())
                        self.allPins.append(pinDict)
                    
                for pin in self.publicPins():
                    try:
                        pinDict = db.to_dict(pin)
                        pinDict["id"] = pin.key().id()
                        pinDict["x"] = self.board.getPinXLocation(pin.key().id())
                        pinDict["y"] = self.board.getPinYLocation(pin.key().id())
                        self.boardPinArray.index(pinDict)
                    except Exception:
                        pinDict = db.to_dict(pin)
                        pinDict["id"] = pin.key().id()
                        pinDict["x"] = self.board.getPinXLocation(pin.key().id())
                        pinDict["y"] = self.board.getPinYLocation(pin.key().id())
                        self.allPins.append(pinDict)
                    
            self.jsonDictionary['publicPins'] = self.allPins;

            self.response.headers["Content-Type"] = "application/json"
            self.response.out.write(json.dumps(self.jsonDictionary, default=date_handler))
            return
        elif self.extension == None:
            if not self.loggedIn and self.board.private:
                self.redirectToHome()
                return
            
            self.templateValues = {'title': 'Board'}
            self.templateValues['boardID'] = self.ID
            self.basicSetup()
            if self.board == None:
                self.templateValues['notFound'] = True
                self.templateValues['title'] = "Error"
            else:
                self.templateValues['notFound'] = False
                self.templateValues['title'] = self.board.name;
                self.templateValues['board'] = self.board
                if not self.loggedIn:
                    self.templateValues['isEditable'] = False
                else:
                    if self.board.owner == self.user.user_id():
                        self.templateValues['isEditable'] = True
                    else:
                        self.templateValues['isEditable'] = False
                    pins = Pin.all();
                    pins.filter("owner =", self.user.user_id())
                    self.templateValues['userPins'] = pins
            self.setTemplate("boardDetails.html")  

        else:
            self.generateNotFoundError()
            return
        
        
    def post(self, boardID):
        self.defineUser()
        self.key = db.Key.from_path('Board', long(boardID))
        self.board = db.get(self.key)
        if self.board.owner !=  self.user.user_id():
            self.error(401)
            self.response.out.write("<html><h1>401 Invalid Rights</h1>You do not have the rights to access this data</html>")
            return
        if self.request.get("method") == "Delete":
            db.delete(self.key)
            self.redirect("/board")
            return
        elif self.request.get("method") == "AddPin":
            key = db.Key.from_path('Pin', long(self.request.get("pinID")))
            self.board.pins.append(key);
            self.board.addLocation(long(self.request.get("pinID")),0,0)
            self.board.put()
            self.error(200)
            self.response.out.write("Success")
#            self.redirect("/board/"+str(self.board.key().id()))
            return
        elif self.request.get("method") == "RemovePin":
            key = db.Key.from_path('Pin', long(self.request.get("pinID")))
            self.board.pins.remove(key)
            self.board.removeLocation(long(self.request.get("pinID")))
            self.board.put();
            self.error(200)
            self.response.out.write("Success")
            #self.redirect("/board/"+str(self.board.key().id()))
            return
        elif self.request.get("method") == "saveName":
            self.board.name = self.request.get("name");
            self.board.put()
            self.error(200)
            self.response.out.write(self.board.name)
            return;
        elif self.request.get("method") == "privateChanged":
            self.board.setPrivateStatus(self.request.get("private"))
            self.board.put()
            self.error(200)
            self.response.out.write(self.board.private)
            return;
        elif self.request.get("method") == "UpdatePinLocation":
            self.board.updatePinLocation(self.request.get("pinID"),self.request.get("x"),self.request.get("y"))
            self.board.put()
            self.error(200)
            self.response.out.write(json.dumps(self.board.locations))
            return;
        else:
            self.board.name = self.request.get("name")
            self.board.setPrivateStatus(self.request.get("private"))
            self.board.put()
            self.redirect("/board/"+str(self.board.key().id()))
            return
        
class BoardCanvasDetails(Universal):          
    def get(self, urlValue):
        self.checkLogin()
        self.key = db.Key.from_path('Board', long(urlValue))
        self.board = db.get(self.key)
        if not self.loggedIn and self.board.private:
                self.redirectToHome()
                return
            
        self.templateValues = {'title': 'Board'}
        self.templateValues['boardID'] = urlValue
        self.basicSetup()
        if self.board == None:
            self.templateValues['notFound'] = True
            self.templateValues['title'] = "Error"
        else:
            self.templateValues['notFound'] = False
            self.templateValues['title'] = self.board.name;
            self.templateValues['board'] = self.board
            if not self.loggedIn:
                self.templateValues['isEditable'] = False
            else:
                if self.board.owner == self.user.user_id():
                    self.templateValues['isEditable'] = True
                else:
                    self.templateValues['isEditable'] = False
                pins = Pin.all();
                pins.filter("owner =", self.user.user_id())
                self.templateValues['userPins'] = pins
        self.setTemplate("boardCanvasDetails.html")  
            
app = webapp2.WSGIApplication([('/', HomePage),
                             ('/pin.json', PinIndex),('/pin', PinIndex),('/pin/(.*)', PinDetails), 
                             ('/board', BoardIndex),('/board/(.*)', BoardDetails),
                             ('/canvas/(.*)',BoardCanvasDetails)],
                             debug=True)