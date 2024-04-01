"""
PLP Week 4 min-project

Learn how to load json data into a python dictionary
Create a function that returns a definition of a word
Consider a condition that the entered word is not in a dictionary
Consider input from user having different cases – upper/ lower case or mixed eg: RAIN/rain/RaIN
Make your dictionary program more intelligent incase users input a word with wrong spelling the program should be able to suggest the word that might be intended.
eg . pott instead of pot or rainn instead of rain.
Tip: use difflib library here
"""

# pip install orjson
import orjson
from difflib import get_close_matches


class Dictionary:
    """dictionary that gets difinations from a JSON file"""

    __slots__ = (
        "word_definitions",
        "dictfile",
        "words",
        "case",
    )

    def __init__(self, dictfile: str, words_case=str.lower):
        # store filename for future ref
        self.dictfile = dictfile
        # function to change word case
        self.case = words_case
        # read dictfile on startup
        self._read_file()

    def _read_file(self):
        """read dictfile and update dictionary"""
        with open(self.dictfile, "rb") as file:
            # get words and definitions
            self.word_definitions: dict = orjson.loads(file.read())
        # get words for suggestions
        self.words = list(self.word_definitions.keys())

    def search(self, word: str) -> str | None:
        """search the definition of word in dictionary"""
        # if definition is None; suggest a word that's close
        word = self.case(word)
        if definition := self.word_definitions.get(word):
            return definition

    def suggest(self, word: str, **kwargs):
        """use difflib to suggest close words to word"""
        word = self.case(word)
        matches = get_close_matches(word, self.words, **kwargs)
        return matches

    def change_file(self, filename: str):
        """change dictfile during runtime"""
        self.dictfile = filename
        self._read_file()
