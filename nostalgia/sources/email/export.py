import json
import logging
import os

import just
from imap_tools import MailBox

log = logging.getLogger(__name__)


class ImapExport(object):
    @staticmethod
    def write(filename, data):
        dirname = os.path.dirname(filename)
        os.makedirs(dirname, exist_ok=True)
        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=2, sort_keys=True))

    def __init__(self, hostname, username, password):
        self._validate_constructor_arguments(hostname, username, password)
        self.hostname = hostname
        self.username = username
        self.password = password

        self.root = just.make_path("~/nostalgia_data/input/imap")

    def filename(self, *args):
        return os.path.join(self.root, self.hostname, *args)

    def walk_folder(self, mailbox, folder_name):
        mails = []
        mailbox.folder.set(folder_name)
        for msg in mailbox.fetch(mark_seen=False):
            mails.append(
                {
                    "from": msg.from_,
                    "to": msg.to,
                    "subject": msg.subject,
                    "text": msg.text,
                    "sent_date": msg.date.isoformat(),
                }
            )
        return mails

    def walk_folders(self):
        with MailBox(self.hostname).login(self.username, self.password) as mailbox:
            for folder in mailbox.folder.list():
                folder_name = folder["name"]
                filename = self.filename("{}.json".format(folder_name.lower()))

                if not os.path.isfile(filename):
                    log.info("Downloading {}".format(filename))
                    mails = self.walk_folder(mailbox, folder_name)
                    self.write(filename, mails)
                else:
                    log.info("Cached {}".format(filename))

    def _validate_constructor_arguments(self, hostname, username, password):
        if hostname is None:
            raise TypeError("Missing hostname")

        if username is None:
            raise TypeError("Missing username")

        if password is None:
            raise TypeError("Missing password")
