# Code from http://pymotw.com/2/smtpd/
# Code from https://github.com/trentrichardson/Python-Email-Dissector/blob/master/EDHelpers/EDServer.py
# Updated to use aiosmtpd for Python 3.13+ compatibility

import base64
from email.parser import Parser
import time
from common import helpers
# Line removed as the `Controller` import is unused.
from aiosmtpd.handlers import Message


class CustomSMTPServer(Message):

    def handle_message(self, message):
        # Extract peer information from the message envelope
        peer = f"{message.get('X-Peer', 'unknown')}"
        mailfrom = message.get('From', 'unknown')
        rcpttos = message.get('To', 'unknown')
        
        print(('Receiving message from:', peer))
        print(('Message addressed from:', mailfrom))
        print(('Message addressed to  :', rcpttos))
        print(('Message length        :', len(str(message))))

        loot_directory = os.path.join(helpers.ea_path(), 'data')

        # Convert message to string for parsing
        data = str(message)
        
        p = Parser()
        msgobj = p.parsestr(data)
        for part in msgobj.walk():
            attachment = self.email_parse_attachment(part)
            if type(attachment) is dict and 'filedata' in attachment:
                    decoded_file_data = base64.b64decode(attachment['filedata'])
                    attach_file_name = attachment['filename']
                    with open(loot_directory + "/" + attach_file_name, 'wb') as attached_file:
                        helpers.received_file(attach_file_name)
                        attached_file.write(decoded_file_data)
            else:
                file_name = "SMTP-"
                current_date = time.strftime("%m/%d/%Y")
                current_time = time.strftime("%H:%M:%S")
                file_name += current_date.replace("/", "") +\
                    "_" + current_time.replace(":", "") + "email_data.txt"

                with open(loot_directory + "/" + file_name, 'a') as email_file:
                    #email_file.write('METADATA: File from - ' + str(peer) + '\n\n')
                    email_file.write(data)
        return

    def email_parse_attachment(self, message_part):

        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition and dispositions[0].lower() == "attachment"):
                attachment = {
                        'filedata': message_part.get_payload(),
                        'content_type': message_part.get_content_type(),
                        'filename': "default"
                    }
                for param in dispositions[1:]:
                    name,value = param.split("=")
                    name = name.strip().lower()

                    if name == "filename":
                        attachment['filename'] = value.replace('"','')

                return attachment

        return None
