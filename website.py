import cPickle as pickle
import webapp2
import jinja2
import os
import random

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def loadoutSortOrder(key):
    key = key["item_slot"]
    if key == "primary": return 0
    elif key == "secondary": return 1
    elif key == "pda2": return 2
    elif key == "melee": return 3
    elif key == "building": return 4
    elif key == "pda": return 5
    else: return 6

def readCache():
    f = open("loadoutDB.p", 'rb')
    data = pickle.load(f)
    f.close()
    return data

class MainPage(webapp2.RequestHandler):
    def __init__(self, request, response):
        self.initialize(request, response)
        self.data = readCache()
    def get(self):
        classname = random.choice(self.data.keys())
        items = []
        for slotitems in self.data[classname].itervalues():
            items.append(random.choice(slotitems))
        items.sort(key=loadoutSortOrder)
        template_values = {
            'classname': classname,
            'items': items
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)])
