# -*- coding: UTF-8 -*-
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import options

class XMPPHandler(webapp.RequestHandler):
    def post(self):
        message = (xmpp.Message(self.request.POST))
        gid = message.sender
        mes = message.body
        if gid.find('/') != -1:
            gid = gid[:gid.find('/')]
        gid = gid.lower()
        options.params_handler(mes, gid)

application = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
