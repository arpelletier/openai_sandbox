import openai
import sys
import os
sys.path.append('../')
from config import OPENAI_KEY

def get_log_file(directory):
    """
    Find the directory for the logs and return the relevant 
    file that needs to be written to.
    """
    try:
        # Create the output directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Find the next available log file
        log_file = None
        i = 0
        while True:
            log_file = os.path.join(directory, f"log_{i}.txt")
            if not os.path.exists(log_file):
                break
            i += 1

        return log_file
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def write_to_log(log_file, text):
    """Using a log file, write text to it."""
    try:
        with open(log_file, 'a') as file:
            file.write(text + '\n')
    except Exception as e:
        print(f"An error occured: {str(e)}")

class OpenAI_API():

    def __init__(self):
        openai.api_key = OPENAI_KEY
        self.chat_model = None
        temp = self.get_chat_model()
        self.chat_model = temp
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def get_chat_model(self):
        if self.chat_model:
            return self.chat_model
        
        messages = [{"role": "user", "content": "Hello"}]
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        return chat_completion

    def call_openai_api(self, user_input):
        try:
            response = self.chat_model['choices'][0]['message']['content']

            return response
        except Exception as e:
            return str(e)
    

    def parse_message(self, chat_completion):
        """
        Parse message after the API has returned a call. 
        Return the contents of the message to be more readable.
        """
        message = chat_completion['choices'][0]['message']

        role = message['role'].capitalize()
        content = message['content']

        return "%s: %s"%(role,content)
    
    def clear_context(self):
        """Use for restarting next instances"""
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    def add_context(self,context_message: str):
        """Add additional information to context"""
        self.messages.append({"role": "assistant", "content": context_message})
    
    def get_context(self):
        return self.messages
    
    def get_context_length(self):
        return len(self.messages)

    def single_chat(self, user_input, timeout_threshold=100):
        self.messages.append({"role": "user", "content": user_input})
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
        message = self.parse_message(chat_completion)
        # Write to log as well
        log_folder = os.path.join('../chat_log')
        log_file = get_log_file(log_folder)
        write_to_log(log_file, "User: "+ user_input)
        write_to_log(log_file, message)
        return message, self.messages


# temp = OpenAI_API()
# chat_temp = temp.get_chat_model()
# import pdb;pdb.set_trace()

if __name__ == "__main__":
    x = OpenAI_API()
    print(x.single_chat("What is the square root of 2?"))


