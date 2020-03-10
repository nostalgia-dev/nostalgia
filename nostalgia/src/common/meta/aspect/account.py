from src.common.infrastructure.nlp import nlp
from src.common.meta.aspect import Aspect

class Account(Aspect):
    @nlp("filter", "by me", "i", "my")
    def by_me(self):
        return self
