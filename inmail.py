from __future__ import with_statement
from google.appengine.api import files
from google.appengine.ext import blobstore
import logging, email, time
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import taskqueue


class LogSenderHandler(InboundMailHandler):


    def receive(self, mail_message):

        logging.info('INMAIL_TEST handler')
        logging.info("Received a message from: %s, to: %s" % (mail_message.sender, mail_message.to))
        logging.info("mail date: %s" % mail_message.date)
        logging.info("subject: %s" % mail_message.subject)
        
        data = mail_message.original.as_string(unixfrom=True)
        logging.info(data)

def main():
    application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

