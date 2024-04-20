import base64
import httpx
import json
import os
from datetime import datetime

def _extract_texts(content):
    if isinstance(content, str):
        return [content]
    elif isinstance(content, list):
        return next((item["text"] for item in content if item["type"] == "text"), "")
    return []

def _contains_query(messages, query):
    """ Check if any message contains the query text. """
    lower_query = query.lower()
    for message in messages:
        texts = _extract_texts(message['content'])
        for text in texts:
            if lower_query in text.lower():
                return True
    return False

class BaseChat:
    def __init__(self):
        self.messages = []
        self.save_folder = ''

    def add_message(self, role, text):
        self.messages.append({"role": role, "content": text})
    
    def reset_context(self):
        self.messages = []
    
    def get_messages(self):
        return self.messages

    def save(self):
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

    def load(self, file_name):
        file_path = os.path.join(self.save_folder, file_name)
        if not os.path.exists(file_path):
            print(f"No file found with name {file_name}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            self.messages = json.load(f)
        print(f"Chat loaded from {file_path}")
        return self.messages

    def list(self):
        # List all files in the save folder
        if not os.path.exists(self.save_folder):
            print("Save folder not found.")
            return []

        # Retrieve the list of files and sort them in descending alphanumeric order
        files = os.listdir(self.save_folder)
        files.sort(reverse=True)  # Set reverse=True to sort in descending order

        return files

    def search(self, query):
        matching_files = []
        for filename in os.listdir(self.save_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(self.save_folder, filename)
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    if _contains_query(data, query):
                        matching_files.append(filename)
        return matching_files

    def match(self, input_string):
        input_words = input_string.rstrip('.?').lower().split()

        for filename in os.listdir(self.save_folder):
            if filename.endswith('.json'):
                clean_filename = filename[:-5]
                hyphen_index = clean_filename.find('-')
                if hyphen_index != -1:
                    words_part = clean_filename[hyphen_index+1:]
                else:
                    words_part = clean_filename

                filename_words = words_part.lower().split('-')
                
                num_filename_words = len(filename_words)
                
                if len(input_words) >= num_filename_words:
                    if input_words[:num_filename_words] == filename_words:
                        return filename
        return None

class GptChat(BaseChat):
    def __init__(self):
        self.messages = []
        self.save_folder = "openai_chats"

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

class ClaudeChat(BaseChat):
    def __init__(self):
        self.messages = []
        self.system = ""
        self.save_folder = "claude_chats"  # Define a folder for saving chats

    def set_system(self, system):
        self.system = system

    def get_system(self):
        return self.system
    
    def reset_context(self):
        self.messages = []
        self.system = ""

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

    def save(self):
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

    def load(self, file_name):
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
    
