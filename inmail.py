from __future__ import with_statement
import files
import uuid
import logging, email, time
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import taskqueue


class LogSenderHandler(InboundMailHandler):


    def receive(self, mail_message):
        filename= '/inmail/' + str(uuid.uuid4())
        logging.info('INMAIL_TEST handler')
        logging.info("Received a message from: %s, to: %s" % (mail_message.sender, mail_message.to))
        logging.info("mail date: %s" % mail_message.date)
        logging.info("subject: %s" % mail_message.subject)
        logging.info("filename %s" % filename)
        data = mail_message.original.as_string(unixfrom=True)

        files.write_file(filename,data)

        taskqueue.add(url='/task/incoming_email/', params={'filename':filename})

def main():
    application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()

