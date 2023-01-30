#!/bin/bash

clear
echo "[*] Installing Egress-Assess Dependencies..."
apt update
apt -y install smbclient

echo "[*] Installing python3-pip"
apt -y install python3-pip

echo "[*] Installing scapy"
pip3 install scapy

echo "[*] Installing Paramiko"
pip3 install paramiko

echo "[*] Installing Crypto"
pip3 install crypto --force

echo "[*] Installing ecdsa"
pip3 install ecdsa

echo "[*] Installing pyasn1"
pip3 install pyasn1

echo "[*] Installing dnspython"
pip3 install dnspython

echo "[*] Installing impacket"
pip3 install impacket

echo "[*] Installing pyftpdlib..."
pip3 install pyftpdlib
python setup.py install

echo "[*] Installing cryptography"
pip3 install cryptography --force

echo "[*] Installing dnslib"
pip3 install dnslib

echo "[*] Installing PyOpenSSL"
pip3 install pyopenssl

echo "[*] Installing PySendFile"
pip3 install pysendfile

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
