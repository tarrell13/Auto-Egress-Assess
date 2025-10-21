'''

This is the code for the web server

'''

import os
import socket
import ssl
import subprocess
import requests
import sys
from common import helpers
from protocols.servers.serverlibs.web import base_handler
from protocols.servers.serverlibs.web import threaded_http
from threading import Thread


class Server:

    def __init__(self, cli_object):
        self.protocol = "https"
        self.arguments = cli_object
        if cli_object.server_port:
            self.port = int(cli_object.server_port)
        else:
            self.port = 443

    def negotiatedServe(self):
        try:
            # bind to all interfaces
            Thread(target=self.serve_on_port).start()
        # handle keyboard interrupts
        except KeyboardInterrupt:
            sys.exit()

    def serve(self):
        try:
            print("[*] Starting web (https) server...")
            # bind to all interfaces
            Thread(target=self.serve_on_port).start()
            print(("[*] Web server is currently running on PORT %s" %str(self.port)))
        # handle keyboard interrupts
        except KeyboardInterrupt:
            print("[!] Rage quiting, and stopping the web server!")
        return

    def serve_on_port(self):
        try:
            cert_path = helpers.ea_path() +\
                '/protocols/servers/serverlibs/web/server.pem'
            
            # Check if certificate exists, if not create a self-signed one
            if not os.path.exists(cert_path):
                print("[*] SSL certificate not found. Creating self-signed certificate...")
                self._create_self_signed_cert(cert_path)
            
            server = threaded_http.ThreadingHTTPServer(
                ("0.0.0.0", self.port), base_handler.GetHandler)
            
            # Use modern SSL context instead of deprecated ssl.wrap_socket
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            # Load combined cert and key file (server.pem contains both)
            context.load_cert_chain(cert_path, cert_path)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            
            server.serve_forever()
        except socket.error:
            if self.arguments.negotiation:
                requests.get("http://localhost:5000/send-status?error=True&protocol=%s" % self.protocol)
            else:
                print(("[*][*] Error: Port %s is currently in use!" % self.port))
                print("[*][*] Error: Please restart when port is free!\n")
                sys.exit()
        except KeyboardInterrupt:
            sys.exit(0)

        return

    def _create_self_signed_cert(self, cert_path):
        """Create a self-signed certificate if one doesn't exist"""
        import subprocess
        
        cert_dir = os.path.dirname(cert_path)
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
        
        # Create self-signed certificate
        cmd = [
            'openssl', 'req', '-new', '-x509', '-keyout', cert_path, 
            '-out', cert_path, '-days', '365', '-nodes', '-subj',
            '/C=US/ST=State/L=City/O=Organization/CN=localhost'
        ]
        
        try:
            subprocess.run(cmd, check=True, cwd=cert_dir, 
                         capture_output=True, text=True)
            print(f"[*] Created self-signed certificate: {cert_path}")
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to create certificate: {e}")
            print("[!] Please run the setup script or create certificate manually")
            sys.exit(1)
