# -*- coding: UTF-8 -*-
from google.appengine.ext import webapp
from google.appengine.api import xmpp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import options

class XMPPHandler(webapp.RequestHandler):
    def get(self):
        result = db.GqlQuery("SELECT * FROM users")[0]
        gid = result.gid
        options.auto_refresh(gid)

application = webapp.WSGIApplication([('/data', XMPPHandler)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
