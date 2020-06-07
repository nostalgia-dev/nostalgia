import os
import shutil

import just
from nostalgia.ndf import NDF


class Twitter(NDF):
    vendor = "twitter"
    ingest_settings = {"ingest_glob": "~/Downloads/twitter-20*-*.zip", "recent_only": False, "delete_existing": False}

    @classmethod
    def ingest(cls):
        super().ingest()
        Twitter._transform_ad_engagement_source()
        Twitter._transform_connected_applications_source()
        Twitter._transform_device_token_source()
        Twitter._transform_dm_source()
        Twitter._transform_email_changed_source()
        Twitter._transform_ip_audit_source()
        Twitter._transform_like_source()
        Twitter._transform_tweet_source()

    @classmethod
    def _transform_ad_engagement_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/ad-engagements.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/ad-engagements.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_connected_applications_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/connected-application.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/connected-application.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_dm_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/direct-messages.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/direct-messages.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_device_token_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/device-token.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/device-token.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_email_changed_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/email-address-change.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/email-address-change.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_ip_audit_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/ip-audit.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/ip-audit.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_like_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/like.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/like.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_tweet_source(cls):
        from_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/tweet.js")
        to_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/tweet.json")
        Twitter._transform_js_file(from_path, to_path)

    @classmethod
    def _transform_js_file(cls, from_path, to_path):
        # Kudos https://stackoverflow.com/a/14947384
        from_file = open(from_path, "r")
        line = from_file.readline()

        # Kudos https://stackoverflow.com/a/33141629
        # replace first line
        line = line[line.find("[") :]

        to_file = open(to_path, "w")
        to_file.write(line)

        shutil.copyfileobj(from_file, to_file)
        from_file.close()
        to_file.close()
