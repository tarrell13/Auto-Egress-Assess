'''

This is the web client code

'''

import ssl
import sys
import urllib.request, urllib.error, urllib.parse


class Client:

    def __init__(self, cli_object):
        self.data_to_transmit = ''
        self.remote_server = cli_object.ip
        self.protocol = "https"
        if cli_object.client_port is None:
            self.port = 443
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
            self.port = int(config["https"]["port"])

        print("[+] Sending HTTPS data")
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        if not self.file_transfer:
            url = "https://" + self.remote_server + ":" + str(self.port) + "/post_data.php?protocol=https"

            # Post the data to the web server at the specified URL
            try:
                f = urllib.request.urlopen(url, data=data_to_transmit.encode(), context=context)
                f.close()
                print("[*] File sent!!!")
            except urllib.error.URLError:
                print(("[*] Error: Web server may not be active on " + self.remote_server))
                print("[*] Error: Please check server to make sure it is active!")
                sys.exit()
        else:
            url = "https://" + self.remote_server + ":" + str(self.port) + "/post_file.php"

            try:
                data_to_transmit = self.file_transfer + ".:::-989-:::." + data_to_transmit
                f = urllib.request.urlopen(url, data=data_to_transmit.encode(), context=context)
                f.close()
                print("[*] File sent!!!")
            except urllib.error.URLError:
                print(("[*] Error: Web server may not be active on " + self.remote_server))
                print("[*] Error: Please check server to make sure it is active!")
                sys.exit()

        return

    def transmit(self, data_to_transmit):

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        if not self.file_transfer:
            url = "https://" + self.remote_server + ":" + str(self.port) + "/post_data.php?protocol=https"

            # Post the data to the web server at the specified URL
            try:
                f = urllib.request.urlopen(url, data=data_to_transmit.encode(), context=context)
                f.close()
                print("[*] File sent!!!")
            except urllib.error.URLError:
                print(("[*] Error: Web server may not be active on " + self.remote_server))
                print("[*] Error: Please check server to make sure it is active!")
                sys.exit()
        else:
            url = "https://" + self.remote_server + ":" + str(self.port) + "/post_file.php"

            try:
                data_to_transmit = self.file_transfer + ".:::-989-:::." + data_to_transmit
                f = urllib.request.urlopen(url, data=data_to_transmit.encode(), context=context)
                f.close()
                print("[*] File sent!!!")
            except urllib.error.URLError:
                print(("[*] Error: Web server may not be active on " + self.remote_server))
                print("[*] Error: Please check server to make sure it is active!")
                sys.exit()

        return
