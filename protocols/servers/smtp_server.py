'''

This is a SMTP server module.  This was based on code made available at:
http://pymotw.com/2/smtpd/

'''

import asyncore
import os
import socket
import sys
import requests
from common import helpers
from protocols.servers.serverlibs.smtp import smtp_class


class Server:

    def __init__(self, cli_object):

        self.protocol = "smtp"
        if cli_object.server_port:
            self.port = int(cli_object.server_port)
        else:
            self.port = 25

    def negotiatedServe(self):

        exfil_directory = os.path.join(helpers.ea_path(), "data/")

        if not os.path.isdir(exfil_directory):
            os.makedirs(exfil_directory)

        try:
            smtp_server = smtp_class.CustomSMTPServer(('0.0.0.0', self.port), None)
        except socket.error:
            requests.get("http://localhost:5000/send-status?error=True&protocol=%s" %self.protocol)

        try:
            asyncore.loop()
        except KeyboardInterrupt:
            requests.get("http://localhost:5000/send-status?stop=True&protocol=%s" %self.protocol)
            sys.exit()

        return

    def serve(self):

        print("[*] SMTP Service Started")
        exfil_directory = os.path.join(helpers.ea_path(), "data/")

        if not os.path.isdir(exfil_directory):
                os.makedirs(exfil_directory)

        try:
            smtp_server = smtp_class.CustomSMTPServer(('0.0.0.0', self.port), None)
        except socket.error:
            print(("[*] Error: Port %d is currently in use!" % self.port))
            print("[*] Error: Please re-start when not in use.")
            sys.exit()

        try:
            asyncore.loop()
        except KeyboardInterrupt:
            print("[*] Shutting down SMTP server...")
            sys.exit(0)

        return
