from enchant.tokenize import Filter


class Names(Filter):
    """If a word start with a Capital letter ignore it"""

    def _skip(self, word):
        return word[0].isupper()
