'''

This is a SMTP server module.  This was based on code made available at:
http://pymotw.com/2/smtpd/
Updated to use aiosmtpd for Python 3.13+ compatibility

'''

import os
import sys
import requests
import time
from common import helpers
from protocols.servers.serverlibs.smtp import smtp_class
from aiosmtpd.controller import Controller


class Server:

    def __init__(self, cli_object):

        self.protocol = "smtp"
        if cli_object.server_port:
            self.port = int(cli_object.server_port)
        else:
            self.port = 25
        self.controller = None

    def _start_and_run_server(self, error_callback, stop_callback, exit_code):
        exfil_directory = os.path.join(helpers.ea_path(), "data/")

        if not os.path.isdir(exfil_directory):
            os.makedirs(exfil_directory)

        try:
            handler = smtp_class.CustomSMTPServer()
            self.controller = Controller(handler, hostname='0.0.0.0', port=self.port)
            self.controller.start()
        except OSError:
            requests.get("http://localhost:5000/send-status?error=True&protocol=%s" %self.protocol)
            return

        try:
            # Keep the server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            requests.get("http://localhost:5000/send-status?stop=True&protocol=%s" %self.protocol)
            if self.controller:
                self.controller.stop()
            sys.exit()

        return

    def negotiatedServe(self):

        exfil_directory = os.path.join(helpers.ea_path(), "data/")

        if not os.path.isdir(exfil_directory):
            os.makedirs(exfil_directory)

        try:
            handler = smtp_class.CustomSMTPServer()
            self.controller = Controller(handler, hostname='0.0.0.0', port=self.port)
            self.controller.start()
        except OSError:
            requests.get("http://localhost:5000/send-status?error=True&protocol=%s" % self.protocol)
            return

        try:
            # Keep the server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            requests.get("http://localhost:5000/send-status?stop=True&protocol=%s" % self.protocol)
            if self.controller:
                self.controller.stop()
            sys.exit()

        return

    def serve(self):

        print("[*] SMTP Service Started")
        exfil_directory = os.path.join(helpers.ea_path(), "data/")

        if not os.path.isdir(exfil_directory):
                os.makedirs(exfil_directory)

        try:
            handler = smtp_class.CustomSMTPServer()
            self.controller = Controller(handler, hostname='0.0.0.0', port=self.port)
            self.controller.start()
            print(f"[*] SMTP server listening on port {self.port}")
        except OSError:
            print(("[*] Error: Port %d is currently in use!" % self.port))
            print("[*] Error: Please re-start when not in use.")
            sys.exit()

        try:
            # Keep the server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[*] Shutting down SMTP server...")
            if self.controller:
                self.controller.stop()
            sys.exit(0)

        return
