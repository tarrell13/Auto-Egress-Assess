#!/bin/bash

echo "[*] Generating Egress-Assess SSH Key"
ssh-keygen -t rsa -f ../protocols/servers/serverlibs/sftp/egress_rsa
echo
cd ../protocols/servers/serverlibs/web
clear
echo "[*] Generating SSL Certificate"
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
echo
echo
echo "[*] Install complete!"
echo "[*] Enjoy Egress-Assess!"
