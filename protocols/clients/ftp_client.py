'''

This is the ftp client code

'''

import os
import socket
import requests
import sys
from common import helpers
from ftplib import FTP
from ftplib import error_perm


class Client:

    def __init__(self, cli_object):
        self.protocol = "ftp"
        self.remote_server = cli_object.ip
        self.username = cli_object.username
        self.password = cli_object.password

        if cli_object.client_port is None:
            self.port = 21
        else:
            self.port = cli_object.client_port
        if cli_object.file is None:
            self.file_transfer = False
        else:
            if "/" in cli_object.file:
                self.file_transfer = cli_object.file.split("/")[-1]
            else:
                self.file_transfer = cli_object.file

    def negotiatedTransmit(self, data_to_transmit,config=None):

        if config:
            self.username = config["ftp"]["username"]
            self.password = config["ftp"]["password"]
            self.port = int(config["ftp"]["port"])

        print("[+] Sending FTP Data")

        try:
            ftp = FTP()
            ftp.connect(self.remote_server, self.port)
        except socket.gaierror:
            print("[*] Error: Cannot connect to FTP server.  Checking provided ip!")
            sys.exit()
        except socket.timeout:
            print("[*] Error: Connection to FTP server timed out!")
            sys.exit()
        except ConnectionRefusedError:
            print("[*] Error: FTP server refused connection!")
            sys.exit()

        try:
            ftp.login(self.username, self.password)
        except error_perm:
            print("[*] Error: Username or password is incorrect!  Please re-run.")
            sys.exit()

        # Set passive mode to False to avoid NAT/firewall issues
        ftp.set_pasv(False)

        if not self.file_transfer:
            ftp_file_name = helpers.writeout_text_data(data_to_transmit, protocol="FTP")
            try:
                with open(helpers.ea_path() + "/" + ftp_file_name, 'rb') as f:
                    ftp.storbinary("STOR " + ftp_file_name, f)
                os.remove(helpers.ea_path() + "/" + ftp_file_name)
            except IOError as e:
                print(f"[*] Error reading file: {e}")
                sys.exit()
        else:
            try:
                with open(self.file_transfer, 'rb') as f:
                    ftp.storbinary("STOR " + self.file_transfer, f)
            except IOError as e:
                print(f"[*] Error reading file: {e}")
                sys.exit()

        try:
            ftp.quit()
        except:
            # If quit fails, try close
            ftp.close()
        print("[*] File sent!!!")

    def transmit(self, data_to_transmit):

        try:
            ftp = FTP()
            ftp.connect(self.remote_server, self.port)
        except socket.gaierror:
            print("[*] Error: Cannot connect to FTP server.  Checking provided ip!")
            sys.exit()
        except socket.timeout:
            print("[*] Error: Connection to FTP server timed out!")
            sys.exit()
        except ConnectionRefusedError:
            print("[*] Error: FTP server refused connection!")
            sys.exit()

        try:
            ftp.login(self.username, self.password)
        except error_perm:
            print("[*] Error: Username or password is incorrect!  Please re-run.")
            sys.exit()

        # Set passive mode to False to avoid NAT/firewall issues
        ftp.set_pasv(False)

        if not self.file_transfer:
            ftp_file_name = helpers.writeout_text_data(data_to_transmit, protocol="FTP")
            try:
                with open(helpers.ea_path() + "/" + ftp_file_name, 'rb') as f:
                    ftp.storbinary("STOR " + ftp_file_name, f)
                os.remove(helpers.ea_path() + "/" + ftp_file_name)
            except IOError as e:
                print(f"[*] Error reading file: {e}")
                sys.exit()
        else:
            try:
                with open(self.file_transfer, 'rb') as f:
                    ftp.storbinary("STOR " + self.file_transfer, f)
            except IOError as e:
                print(f"[*] Error reading file: {e}")
                sys.exit()

        try:
            ftp.quit()
        except:
            # If quit fails, try close
            ftp.close()
        print("[*] File sent!!!")
