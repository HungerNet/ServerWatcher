import requests

class DiscordBotWebhook:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
    
    def send(self, content: str, **ctx):
        requests.post(
            self.url,
            json={"content": content, **ctx},
            timeout=5
        ).raise_for_status()
