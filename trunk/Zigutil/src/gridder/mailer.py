#!usr/var/env python
# coding=utf-8

import smtplib, socket
import datetime
import os

class MailSentry(object):
    '''Class for creating a sentry object to describe various ongoing issues
    in other classes via email. 
    '''

    def __init__(self, input):
        '''Takes a list argv as parameter with following configuration:
        argv[0] = name of the server (+ port)
        argv[1] = from address
        argv[2:] = to address(es)
        '''
        self.server = input[0]
        self.fromaddr = input[1]
        self.toaddrs = input[2:]
        self.message = None
        
        # Object log
        self.loglist = []

    def sendmail(self, username, password, message):
        '''Method to connect to the SMTP server (using TLS security if
        available) and sending the message through email.'''

        try:
            s = smtplib.SMTP(self.server)
            # Establish TLS
            code = s.ehlo()[0]
            usesmtp = 1
            if not (200 < code < 299):
                usesmtp = 0
                code = s.helo()[0]
                if not (200 <= code <= 299):
                    raise smtplib.SMTPHeloError(code)
            
            if usesmtp and s.has_extn('starttls'):
                self.log("Negotiating TLS...")
                s.starttls()
                code = s.ehlo()[0]
                if not (200 <= code <= 299):
                    self.log("Could not EHLO after STARTTLS.")
                    return 0
                self.log("Using TLS connection.")
            else:
                self.log("Server does not support TLS; using normal connection.")
            try:
                s.login(username, password)
            except smtplib.SMTPException, e:
                self.log("Authentication failed: %s" % e)
                return 0
            # mes = self.getmessage(message)
            s.sendmail(self.fromaddr, self.toaddrs, message)
            self.log('Message: %s' % message)
        except (socket.gaierror, socket.error, socket.herror, 
                smtplib.SMTPException), e:
            self.log("Message may not have been sent: %s" % e)
            return 0
        else:
            self.log("Message succesfully sent.")
            return 1
            
    def getmessage(self, message):
        '''Methdod to create the error/exception report to be sent.'''
        to = 'To: %s\n' % '\n'.join([addr for addr in self.toaddrs])
        fro = 'From: %s \n' % self.fromaddr
        body = 'Message: %s' % message
        return to + fro + body
    
    def log(self, message):
        '''Get cuurent time stamp.'''
        self.loglist.append((datetime.datetime.now().ctime(), message))
        
    def savelog(self, path):
        '''Method for printing the log into a file.'''
        #print os.path.join(path, 'maillog.txt')
        outfile = open(os.path.join(path, 'maillog.txt'), 'a')
        outfile.write('%s' % '-' * 52 + '\n')
        for entry in self.loglist:
            outfile.write('%s: %s\n' % entry)
        outfile.write('%s' % '-' * 52 + '\n')
        outfile.close()

if __name__ == '__main__':
    message = 'Olen niin kuuma, beibi! Saanko TULLA koneellesi? T. LoveMachine'
    argv = ['smtp.helsinki.fi:587', 'joona.lehtomaki@helsinki.fi',
            'kaisa.valimaki@helsinki.fi']
    sentry = MailSentry(argv)
    if sentry.sendmail('jlehtoma', 'nEzz3qvi', message):
        print "Success!"
    else:
        print "Failure..."
    for item in sentry.loglist:
            print item
    sentry.savelog(os.getcwd())     
        