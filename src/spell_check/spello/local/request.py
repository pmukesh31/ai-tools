import requests
import json

class ModelRequest():
    def __init__(self, text, lang='ory'):
        self.text = text
        self.lang = lang  

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
