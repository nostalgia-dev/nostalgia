from nostalgia.times import tz
import pandas as pd
import just
from nostalgia.interfaces.chat import ChatInterface
from nostalgia.data_loading import read_array_of_dict_from_json
from nostalgia.sources.facebook import Facebook

# # # # #


class FacebookChat(Facebook, ChatInterface):
    """# Facebook Chat
       Facebook allows you to export all your data. This source is about the chat between two people using Facebook Messenger.

       ### Obtaining the data
       Go to https://www.facebook.com/settings?tab=your_facebook_information and click "Download your information".

       Make sure to select at least **Messages**, and choose **JSON** format above.

       Afterwards, unpack the ZIP-archive and provide the root folder as "file_path".
       For "user", fill in a subfolder name (e.g. johnsmith_nx44ludqrh)."""

    me = ""
    sender_column = "sender_name"

    @classmethod
    def load(cls, nrows=None):
        file_path = "~/nostalgia_data/input/facebook"
        chat_paths = just.glob(f"{file_path}/messages/inbox/*/message_*.json")
        face = [
            read_array_of_dict_from_json(chat_file, "messages", nrows) for chat_file in chat_paths
        ]
        for df in face:
            senders = df.sender_name.unique()
            if len(senders) == 2:
                df.loc[df.sender_name == senders[0], "receiver_name"] = senders[1]
                df.loc[df.sender_name == senders[1], "receiver_name"] = senders[0]
            elif len(senders) > 2:
                df["receiver_name"] = ", ".join([x for x in senders if isinstance(x, str)])
        face = [x for x in face]
        face = pd.concat(face)
        face = face.reset_index(drop=True).sort_values("timestamp_ms")
        face["time"] = pd.to_datetime(face["timestamp_ms"], unit='ms', utc=True).dt.tz_convert(tz)
        face.drop("timestamp_ms", axis=1, inplace=True)
        face.loc[
            (face["type"] != "Generic") | face["content"].isnull(), "content"
        ] = "<INTERACTIVE>"
        face["path"] = ""
        if "photos" in face:
            not_null = face["photos"].notnull()
            face.loc[not_null, "path"] = [
                file_path + "/" + x[0]["uri"] for x in face[not_null]["photos"]
            ]
        # if "photos" in face and isinstance(face["photos"]):
        #     face["path"] = [x.get("uri") if x else x for x in face["photos"]]
        return cls(face)
