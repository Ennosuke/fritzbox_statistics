from imaplib import IMAP4
import ssl
import email
from datetime import datetime
from os import path
import os


class IMAPMailLoader:
    def __init__(self, server, username, password, file_path, archive_path, tls=True):
        self._server = server
        self._username = username
        self._password = password
        self._path = file_path
        self._archive = archive_path
        self._tls = tls

    def load_emails(self):
        with IMAP4(self._server) as imap:
            if self._tls:
                context = ssl.create_default_context()
                imap.starttls(context)
            imap.login(self._username, self._password)
            imap.select()
            messages = imap.search(None, '(SUBJECT "Nutzungs-")')
            message_ids = messages[1][0].split()
            count_message = len(message_ids)
            new_files = 0
            for message_id in message_ids:
                typ, message_data = imap.fetch(message_id, '(RFC822)')
                message = email.message_from_bytes(message_data[0][1])
                message_date = datetime.strptime(message['date'], '%a, %d %b %Y %H:%M:%S %z')
                file_name = self._path+os.path.sep+message_date.strftime('%Y-%m-%d')+'.html'
                archive = self._archive+os.path.sep+message_date.strftime('%Y-%m-%d')+'.html'
                if path.exists(file_name) or path.exists(archive):
                    continue
                html_payload = message.get_payload()[0].get_payload(decode=True).decode('utf-8')
                with open(file_name, 'w') as f:
                    f.write(html_payload)
                new_files += 1
            print('Found %i messages in total and created %i new files' % (count_message, new_files))
