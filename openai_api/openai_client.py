import openai
import sys
sys.path.append('../')
from config import OPENAI_KEY

class OpenAI_API():

    def __init__(self):
        openai.api_key = OPENAI_KEY
        self.chat_model = None
        temp = self.get_chat_model()
        self.chat_model = temp

    def get_chat_model(self):
        if self.chat_model:
            return self.chat_model
        
        messages = [{"role": "user", "content": "Hello"}]
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        return chat_completion

    def call_openai_api(self,user_input):
        try:
            
            # messages = [{"role": "user", "content": user_input}]
            # chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            # self.chat_model.
            response = self.chat_model['choices'][0]['message']['content']

            return response
        except Exception as e:
            return str(e)
        

temp = OpenAI_API()
chat_temp = temp.get_chat_model()
import pdb;pdb.set_trace()


