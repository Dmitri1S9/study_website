class CharacterException(Exception):
    def __init__(self):
        self.message = "Character Exception, because the character is not found"
    def __str__(self):
        return repr(self.message)

class OpenAIException(Exception):
    def __init__(self):
        self.message = "Problems on OpenAI side"
    def __str__(self):
        return repr(self.message)