# NOTE: This file uses LangChain capabilites in conversing with the user
# NOTE: Here, we add summarization techniques using the transformers library
from openai import OpenAI
import sys
import os
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from transformers import pipeline

sys.path.append('../')
from config import OPENAI_KEY
client = OpenAI(api_key=OPENAI_KEY)

summarizer = pipeline("summarization", model="Falconsai/text_summarization")

NODES = ...
EDGES = ...

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
        self.chat_model = None
        temp = self.get_chat_model()
        self.chat_model = temp

    def get_chat_model(self):
        if self.chat_model:
            return self.chat_model
        
        messages = [{"role": "user", "content": "Hello"}]
        chat_completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
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
        message = chat_completion.choices[0].message

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
    
    def single_chat(self, summarize=False, summarizer_max_length=200, summarizer_min_length=50, do_sampling=False):
        # For a single chat, just write everything that occurs in a conversation in 1 log file
        log_folder = os.path.join('../chat_log')
        log_file = get_log_file(log_folder)
        
        llm = ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_KEY)
        conversation = ConversationChain(llm=llm)

        conv_index = 1

        while True:
            # Collect user input and run conversation
            user_input = input("User Input: ")
            conversation.invoke(user_input)

            # Save LLM response, summarize it, and restore the result  
            llm_response = conversation.memory.chat_memory.messages[conv_index].content
            # If the text is already too short to be summarized, do nothing
            if len(llm_response.split()) > summarizer_max_length:
                summarized_text = summarizer(llm_response, max_length=summarizer_max_length, 
                                         min_length=summarizer_min_length, do_sample=do_sampling)[0]["summary_text"]
                conversation.memory.chat_memory.messages[conv_index].content = summarized_text

            # Document all responses
            write_to_log(log_file, "User or summarized query:\n" + user_input)
            write_to_log(log_file, "---------------------------------------------------------------------------")
            write_to_log(log_file, "LLM response\n" + llm_response)
            write_to_log(log_file, "---------------------------------------------------------------------------")
            write_to_log(log_file, "Summarized text stored in conversation:\n" + conversation.memory.chat_memory.messages[conv_index].content)
            write_to_log(log_file, "---------------------------------------------------------------------------")
            write_to_log(log_file, "ConversationChain messages in memory:\n" + str(conversation.memory.chat_memory.messages))
            write_to_log(log_file, "***************************************************************************")

            # Increase the conversation index
            conv_index += 2

if __name__ == "__main__":
    x = OpenAI_API()
    x.single_chat()



