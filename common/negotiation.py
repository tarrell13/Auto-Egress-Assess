# -*- coding: utf-8 -*-
import hashlib

import flask
from flask import request, jsonify
import random
import json
import sys
import base64
import os
import logging
import string
from common import helpers
import shutil

server = flask.Flask(__name__)
data = {}

class Negotiation(object):

    def __init__(self, arguments, protocols=None):

        global data

        self.arguments = arguments
        self.protocols = protocols
        self.server = None

        if self.arguments.negotiation:
            if os.path.isfile("negotiations.conf"):
                data = json.loads(open("negotiations.conf","r").read())
        return

    def start(self):
        self.GenerateProtocolConfigurations()
        server_information = json.loads(request.get("https://ipinfo.io").content)

        log = logging.getLogger('werkzeug')
        log.disabled = True
        server.name = "Egress Assess - Negotiation Mode\r[+] Negotiations Hosted: http://%s:5000/get-negotiations" %server_information["ip"]
        server.run(host="0.0.0.0")

        print("[!] Client Command to Run Negotiation Mode ")
        print("[*] python3 Egress-Assess.py --negotiation --ip %s --datetype ssn" %server_information["ip"])

    def GenerateProtocolConfigurations(self):

        global data

        for proto in self.protocols:
            password = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(12)])
            # Configure each protocol values depending Protocols being tested
            if proto.protocol.lower() == "ftp":

                if data["ftp"]["password"] == "null":
                    data["ftp"]["password"] = password

                proto.username = data["ftp"]["username"]
                proto.password = data["ftp"]["password"]
                proto.port = int(data["ftp"]["port"])
                data["ftp"]["enabled"] = "True"

            elif proto.protocol.lower() == "smb":

                if data["smb"]["password"] == "null" and data["smb"]["username"] == "null":
                    print("here")
                    data["smb"]["username"] = "null"
                    data["smb"]["password"] = "null"

                elif data["smb"]["password"] == "null" and data["smb"]["username"] != "null":
                    data["smb"]["password"] = password

                if data["smb"]["smb2"] == "True":
                    proto.smb2support = True

                proto.username = data["smb"]["username"]
                proto.password = data["smb"]["password"]
                proto.port = int(data["smb"]["port"])
                data["smb"]["enabled"] = "True"

            elif proto.protocol.lower() == "sftp":
                if data["sftp"]["password"] == "null":
                    data["sftp"]["password"] = password
                proto.username = data["sftp"]["username"]
                proto.password = data["sftp"]["password"]
                proto.port = int(data["sftp"]["port"])
                data["sftp"]["enabled"] = "True"

            elif proto.protocol.lower() == "http":
                proto.port = int(data["http"]["port"])
                data["http"]["enabled"] = "True"

            elif proto.protocol.lower() == "https":
                proto.port = int(data["https"]["port"])
                data["https"]["enabled"] = "True"

            elif proto.protocol.lower() == "icmp":
                data["icmp"]["enabled"] = "True"

            elif proto.protocol.lower() == "dns":
                data["dns"]["enabled"] = "True"
                #data["dns_resolved"]["enabled"] = "True"

            elif proto.protocol.lower() == "smtp":
                proto.port = int(data["smtp"]["port"])
                data["smtp"]["enabled"] = "True"

        return

    def RetrieveServerProtocols(self):
        return

    @server.route('/get-negotiations', methods=['GET'])
    def ServeProtocolInformation():
        print(("[+] Retrieving Negotiations from client: %s" %request.remote_addr))
        return jsonify(data)

    '''
    @server.route("/negotiation-enabled", methods=["GET"])
    def IsEnabled():
        return jsonify(True)
    '''

    @server.route('/send-status', methods=["GET"])
    def CheckInOutput():

        if request.args.get("protocol") and request.args.get("started"):
            print(("[+] %s Server Has Been Started" %request.args.get("protocol").upper()))

        if request.args.get("error"):
            print(("(!) Issues Start %s Server...skipping" %request.args.get("protocol").upper()))

        if request.args.get("stop"):
            print(("[+] %s Server is Stopping" %request.args.get("protocol").upper()))

        if request.args.get("complete") and request.args.get("protocol"):
            print(("[+] %s Data Finished Sending From Client: %s" %(request.args.get("protocol").upper(),request.remote_addr)))

        if request.args.get("protocol") and request.args.get("send"):
            print(("[+] Client %s attempting to send %s data" %(request.remote_addr, request.args.get("protocol").upper())))

        return jsonify({200: "Success"})


    """ API Endpoint needed to signal creation of LOOT Directory """
    @server.route('/create-directory', methods=["GET"])
    def LootCreationDirectory():

        if request.args.get("folder"):

            loot_directory = helpers.PROGRAM_PATH + "/data/%s" % str(request.args.get("folder"))
            if not os.path.isdir(loot_directory):
                os.makedirs(loot_directory)
                print("[+] %s Loot Directory Created" % str(request.args.get("folder")))
            else:
                print("[+] %s Loot Directory Already Exists" % str(request.args.get("folder")))

        return jsonify({200: "Success"})

    @server.route('/move-loot-files', methods=['GET'])
    def MoveLootFile():
        """ Moves the Loot File from Data to Proper RV Directory if Specified """
        if request.args.get("folder") and request.args.get("hash"):
            loot_directory = helpers.PROGRAM_PATH + "/data/%s" % str(request.args.get("folder"))
            encoded_sample = request.headers.get("samples")
            client_file_hash = request.args.get("hash")

            """ Check Hash Data """
            for file in os.listdir(helpers.PROGRAM_PATH + "/data"):
                if os.path.isfile(helpers.PROGRAM_PATH + "/data/" + file):
                    inspection_file = open(helpers.PROGRAM_PATH + "/data/" + file).read()
                    if hashlib.md5(inspection_file.encode()).hexdigest() == client_file_hash:
                        shutil.move(helpers.PROGRAM_PATH + "/data/%s" % file, loot_directory)
                        print("[+] Moving %s into %s" % (file, str(request.args.get("folder"))))

            """ Check Sample Data """
            for file in os.listdir(helpers.PROGRAM_PATH + "/data"):
                if os.path.isfile(helpers.PROGRAM_PATH + "/data/" + file):
                    if file.startswith("SMTP"):
                        inspection_file = open(helpers.PROGRAM_PATH + "/data/" + file).readlines()
                        if base64.b64decode(encoded_sample).decode() == str(inspection_file[9].split(",")[0:5]):
                            shutil.move(helpers.PROGRAM_PATH + "/data/%s" % file, loot_directory)
                            print("[+] Moving %s into %s" % (file, str(request.args.get("folder"))))
                    else:
                        inspection_file = open(helpers.PROGRAM_PATH + "/data/" + file).read()

                        if base64.b64decode(encoded_sample).decode() == str(inspection_file.split(",")[0:5]):
                            shutil.move(helpers.PROGRAM_PATH + "/data/%s" % file, loot_directory)
                            print("[+] Moving %s into %s" % (file, str(request.args.get("folder"))))

        return jsonify({200: "Success"})
