'''
THIS FILE IS A DRAFT AND WILL BE USED TO CHECK HOW TO STORE MEMORY AND CONTEXT.
Chatbots: https://python.langchain.com/docs/use_cases/chatbots/

Sliding window of k=2
Add one message and then make sure that you summarize it with a summarizer

Goal is to test a summarizer 
'''


import openai
import sys
import os
sys.path.append('../')
from config import OPENAI_KEY

from transformers import pipeline
summarizer = pipeline('summarization')
TEXT = """
In the theory of formal languages, the pumping lemma for regular languages is a lemma that describes an essential property of all regular languages. Informally, it says that all sufficiently long strings in a regular language may be pumped—that is, have a middle section of the string repeated an arbitrary number of times—to produce a new string that is also part of the language.

Specifically, the pumping lemma says that for any regular language L L there exists a constant p p such that any string w w in L L with length at least p p can be split into three substrings x x, y y and z z ( w = x y z {\displaystyle w=xyz}, with y y being non-empty), such that the strings x z , x y z , x y y z , x y y y z , . . . {\displaystyle xz,xyz,xyyz,xyyyz,...} constructed by repeating y y zero or more times are still in L L. This process of repetition is known as "pumping". Moreover, the pumping lemma guarantees that the length of x y xy will be at most p p, imposing a limit on the ways in which w w may be split.

Languages with a finite number of strings vacuously satisfy the pumping lemma by having p p equal to the maximum string length in L L plus one. By doing so, zero strings in L L have length greater than p p.

The pumping lemma is useful for disproving the regularity of a specific language in question. It was first proven by Michael Rabin and Dana Scott in 1959,[1] and rediscovered shortly after by Yehoshua Bar-Hillel, Micha A. Perles, and Eli Shamir in 1961, as a simplification of their pumping lemma for context-free languages.[2][3] 
"""

summary = summarizer(TEXT, max_length=200, do_sample=False)
print(summary)














# memory = ConversationBufferWindowMemory(k=1)
# memory.save_context({"input": "hi"}, {"output": "whats up"})
# memory.save_context({"input": "not much you"}, {"output": "not much"})
# print(memory.load_memory_variables({}))



# class OpenAI_API():
#     def __init__(self):
#         openai.api_key = OPENAI_KEY
#         self.chat_model = None
#         temp = self.get_chat_model()
#         self.chat_model = temp
#         self.messages = ConversationBufferWindowMemory(k=3)

#     def get_chat_model(self):
#         if self.chat_model:
#             return self.chat_model
        
#         messages = [{"role": "user", "content": "Hello"}]
#         chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
#         return chat_completion

#     def call_openai_api(self, user_input):
#         try:
#             response = self.chat_model['choices'][0]['message']['content']

#             return response
#         except Exception as e:
#             return str(e)
    

#     def parse_message(self, chat_completion):
#         """
#         Parse message after the API has returned a call. 
#         Return the contents of the message to be more readable.
#         """
#         message = chat_completion['choices'][0]['message']

#         role = message['role'].capitalize()
#         content = message['content']

#         return "%s: %s"%(role,content)
    
#     def clear_context(self):
#         """Use for restarting next instances"""
#         self.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
#     def add_context(self,context_message: str):
#         """Add additional information to context"""
#         self.messages.append({"role": "assistant", "content": context_message})
    
#     def get_context(self):
#         return self.messages
    
#     def get_context_length(self):
#         return len(self.messages)

#     def single_chat(self, user_input, timeout_threshold=100):
#         # Save the context of the message
#         self.messages.


#         self.messages.append({"role": "user", "content": user_input})
#         chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
#         message = self.parse_message(chat_completion)
#         # Write to log as well
#         log_folder = os.path.join('../chat_log')
#         log_file = get_log_file(log_folder)
#         write_to_log(log_file, "User: "+ user_input)
#         write_to_log(log_file, message)
#         return message, self.messages



