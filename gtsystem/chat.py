import base64
import httpx

import json
import os
from datetime import datetime

class GptChat:
    def __init__(self):
        self.messages = []
        self.save_folder = "openai_chats"  # Define a folder for saving chats

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

    def save_chat(self):
        if not self.messages:
            print("No chat to save.")
            return

        # Check and create save folder if it doesn't exist
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        # Create a filename based on the first user message
        first_user_message = next((msg for msg in self.messages if msg["role"] == "user"), None)
        if first_user_message:
            date_prefix = datetime.now().strftime("%y%m%d%H%M%S")
            first_ten_words = ""
            if isinstance(first_user_message["content"], list):  # Handle mixed content type
                text_content = next((item["text"] for item in first_user_message["content"] if item["type"] == "text"), "")
                first_ten_words = "-".join(text_content.split()[:10])
            else:
                first_ten_words = "-".join(first_user_message["content"].split()[:10])
            first_ten_words = first_ten_words.rstrip('.?')  # Clean up filename part
            filename = f"{date_prefix}-{first_ten_words}.json"
            filename = filename.replace("/", "-")  # Ensure filename is valid
        else:
            print("No user messages to determine filename.")
            return

        # Save the messages to a file
        file_path = os.path.join(self.save_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)
        print(f"Chat saved to {file_path}")

    def load_chat(self, file_name):
        file_path = os.path.join(self.save_folder, file_name)
        if not os.path.exists(file_path):
            print(f"No file found with name {file_name}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            self.messages = json.load(f)
        print(f"Chat loaded from {file_path}")
        return self.messages

    def list_chats(self):
        # List all files in the save folder
        if not os.path.exists(self.save_folder):
            print("Save folder not found.")
            return []

        # Retrieve the list of files and sort them in descending alphanumeric order
        files = os.listdir(self.save_folder)
        files.sort(reverse=True)  # Set reverse=True to sort in descending order

        return files

class ClaudeChat:
    def __init__(self):
        self.messages = []
        self.system = ""
        self.save_folder = "claude_chats"  # Define a folder for saving chats

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

    def save_chat(self):
        if not self.messages:
            print("No chat to save.")
            return

        # Check and create save folder if it doesn't exist
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        # Create a filename based on the first user message
        first_user_message = next((msg for msg in self.messages if msg["role"] == "user"), None)
        if first_user_message:
            date_prefix = datetime.now().strftime("%y%m%d%H%M%S")
            first_ten_words = ""
            if isinstance(first_user_message["content"], list):  # Handle mixed content type
                text_content = next((item["text"] for item in first_user_message["content"] if item["type"] == "text"), "")
                first_ten_words = "-".join(text_content.split()[:10])
            else:
                first_ten_words = "-".join(first_user_message["content"].split()[:10])
            first_ten_words = first_ten_words.rstrip('.?')  # Clean up filename part
            filename = f"{date_prefix}-{first_ten_words}.json"
            filename = filename.replace("/", "-")  # Ensure filename is valid
        else:
            print("No user messages to determine filename.")
            return

        # Save the messages to a file
        file_path = os.path.join(self.save_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            save_messages = self.messages
            if self.system != "":
                save_messages.insert(0, {"role": "system", "content": self.system})
            json.dump(self.messages, f, ensure_ascii=False, indent=4)
        print(f"Chat saved to {file_path}")

    def load_chat(self, file_name):
        file_path = os.path.join(self.save_folder, file_name)
        if not os.path.exists(file_path):
            print(f"No file found with name {file_name}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            all_messages = json.load(f)

        # Temporary list to hold messages without the system message
        new_messages = []

        # Iterate through messages and handle system message
        for message in all_messages:
            if message.get('role') == 'system':
                self.system = message['content']
            else:
                new_messages.append(message)

        # Update self.messages without the system message
        self.messages = new_messages

        print(f"Chat loaded from {file_path}")
        return self.messages

    def list_chats(self):
        # List all files in the save folder
        if not os.path.exists(self.save_folder):
            print("Save folder not found.")
            return []

        # Retrieve the list of files and sort them in descending alphanumeric order
        files = os.listdir(self.save_folder)
        files.sort(reverse=True)  # Set reverse=True to sort in descending order

        return files
