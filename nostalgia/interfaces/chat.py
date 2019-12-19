from nostalgia.ndf import NDF
from nostalgia.nlp import nlp


class ChatInterface(NDF):
    __name__ = ""
    me = ""
    sender_column = ""
    _sender_updated = False

    @nlp("filter", "by me", "i", "my")
    def by_me(self):
        return self[self.sender == "me"]

    @nlp("filter", "by the other", "by someone else")
    def by_other(self):
        return self[self.sender != "me"]

    @property
    def sender(self):
        if not self._sender_updated:
            col = self[self.sender_column]
            self.loc[col == self.me, self.sender_column] = "me"
            self._sender_updated = True
        return self[self.sender_column]
