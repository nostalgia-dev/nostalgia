import json
import logging
import os
import re

import just

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
        hostname = self._get_valid_filename(self.hostname)
        email_alias = self._get_valid_filename(self.username.split("@")[0])
        return os.path.join(self.root, hostname, email_alias, *args)

    def walk_folder(self, mailbox, folder_name):
        mails = []
        mailbox.folder.set(folder_name)
        for msg in mailbox.fetch(mark_seen=False):
            try:
                mails.append(
                    {
                        "from": msg.from_,
                        "to": msg.to,
                        "subject": msg.subject,
                        "text": msg.text,
                        "sent_date": msg.date.isoformat(),
                    }
                )
            except TypeError as exc:
                logger.error("Could not append mail for {}".format(folder_name))
                logger.error(exc)
        return mails

    def walk_folders(self):
        from imap_tools import MailBox

        with MailBox(self.hostname).login(self.username, self.password) as mailbox:
            for folder in mailbox.folder.list():
                folder_name = folder["name"]
                filename = self.filename("{}.json".format(self._get_valid_filename(folder_name.lower())))

                if not os.path.isfile(filename):
                    log.info("Downloading {}".format(filename))
                    mails = self.walk_folder(mailbox, folder_name)
                    self.write(filename, mails)
                else:
                    log.info("Cached {}".format(filename))

    # Inspired by https://github.com/django/django/blob/796be5901a67da44e251e092641682cb2d778176/django/utils/text.py#L221-L232
    def _get_valid_filename(self, raw_filename):
        s = str(raw_filename).strip().replace(" ", "_")
        return re.sub(r"(?u)[^-\w.]", "", s)

    def _validate_constructor_arguments(self, hostname, username, password):
        if hostname is None:
            raise TypeError("Missing hostname")

        if username is None:
            raise TypeError("Missing username")

        if password is None:
            raise TypeError("Missing password")
