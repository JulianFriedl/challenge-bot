class CustomAPIError(Exception):
    def __init__(self, message, embed):
        self.message = message
        self.embed = embed
        super().__init__(message)
