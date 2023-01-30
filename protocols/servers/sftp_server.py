'''

This is a ssh server designed to listen for sftp connections
This code came from:

base code came from - https://searchcode.com/codesearch/raw/53300304/

'''

import os
import paramiko
import socket
import requests
import sys
import threading
import time
from common import helpers
from io import StringIO
from protocols.servers.serverlibs.sftp import sftp_classes


class Server:

    def __init__(self, cli_object):
        self.protocol = "sftp"
        self.username = cli_object.username
        self.password = cli_object.password
        self.sftp_directory = helpers.ea_path() + '/data'
        if cli_object.server_port:
            self.port = int(cli_object.server_port)
        else:
            self.port = 22

        """ Pointer to Egress-Assess Generated SSH RSA KEY """
        self.rsa_key = helpers.PROGRAM_PATH + "/protocols/servers/serverlibs/sftp/egress_rsa"

    def accept_client(
            self, client, addr, root_dir, users, host_rsa_key, password):
        usermap = {}
        for u in users:
            usermap[u.username] = u

        host_key_file = open(host_rsa_key, "r")
        host_key = paramiko.RSAKey(file_obj=host_key_file)
        transport = paramiko.Transport(client)
        transport.load_server_moduli()
        transport.add_server_key(host_key)

        impl = sftp_classes.SimpleSftpServer
        transport.set_subsystem_handler(
            "sftp", paramiko.SFTPServer, sftp_si=impl, transport=transport,
            fs_root=root_dir, users=usermap)

        server = sftp_classes.SimpleSSHServer(users=usermap)
        transport.start_server(server=server)
        channel = transport.accept()
        while(transport.is_active()):
            time.sleep(3)

        username = server.get_authenticated_user()
        if username is not None:
            user = usermap[username]
            os.system("svn commit -m 'committing user session for %s' %s" % (username, root_dir + "/" + user.home))
        return

    def negotiatedServe(self):

        loot_path = os.path.join(helpers.ea_path(), "data") + "/"
        # Check to make sure the agent directory exists, and a loot
        # directory for the agent.  If not, make them
        if not os.path.isdir(loot_path):
            os.makedirs(loot_path)

        user_map = [sftp_classes.User(
            username=self.username, password=self.password, chroot=False), ]

        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(10)
        except socket.error:
            requests.get("http://localhost:5000/send-status?error=True&protocol=%s" %self.protocol)
            sys.exit()

        while True:
            try:
                client, addr = server_socket.accept()
                t = threading.Thread(target=self.accept_client, args=[
                    client, addr, self.sftp_directory, user_map,
                    self.rsa_key, self.password])
                t.daemon = True
                t.start()
            except KeyboardInterrupt:
                sys.exit()


    def serve(self):

        loot_path = os.path.join(helpers.ea_path(), "data") + "/"
        # Check to make sure the agent directory exists, and a loot
        # directory for the agent.  If not, make them
        if not os.path.isdir(loot_path):
            os.makedirs(loot_path)

        user_map = [sftp_classes.User(
            username=self.username, password=self.password, chroot=False), ]

        print("[*] Starting SFTP server...")

        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(10)
        except socket.error:
            print(("[*] Error: Port in use! Please restart when port {} is free!".format(self.port)))
            sys.exit()

        print("[*] SFTP server started!\n")

        while True:
            try:
                client, addr = server_socket.accept()
                t = threading.Thread(target=self.accept_client, args=[
                    client, addr, self.sftp_directory, user_map,
                    self.rsa_key, self.password])
                t.daemon = True
                t.start()
            except KeyboardInterrupt:
                print("[*] Shutting down SFTP server...")
                sys.exit(0)

        return
