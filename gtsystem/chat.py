import base64
import httpx

class GptChat:
    def __init__(self):
        self.messages = []

    def add_message(self, role, text):
        self.messages.append({"role": role, "content": text})
    
    def reset_context(self):
        self.messages = []
    
    def get_messages(self):
        return self.messages

    def add_image_message(self, prompt, image_url):
        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                }
            ],
        })

class ClaudeChat:
    def __init__(self):
        self.messages = []
        self.system = ""

    def set_system(self, system):
        self.system = system

    def get_system(self):
        return self.system

    def add_message(self, role, text):
        self.messages.append({"role": role, "content": text})
    
    def reset_context(self):
        self.messages = []
        self.system = ""
    
    def get_messages(self):
        return self.messages

    def add_image_message(self, prompt, image_url):
        image_media_type = "image/jpeg"
        image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": image_data,
                    },
                }
            ],
        })