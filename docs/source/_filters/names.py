from enchant.tokenize import Filter


class Names(Filter):
    def _skip(self, word):
        """If a word start with a Capital letter ignore it."""
        return word[0].isupper()
