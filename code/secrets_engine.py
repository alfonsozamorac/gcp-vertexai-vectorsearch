
class SecretsEngine:

    def __init__(self, path: str):
        self.path = path

    def get_secret(self):
        with open(self.path) as f:
            secret = f.read()
        return secret
