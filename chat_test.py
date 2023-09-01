import os
import openai


def parse_message(chat_completion):

    message = chat_completion['choices'][0]['message']

    role = message['role'].capitalize()
    content = message['content']

    return "%s: %s"%(role,content)


def get_log_file(directory):
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
    try:
        with open(log_file, 'a') as file:
            file.write(text + '\n')
    except Exception as e:
        print(f"An error occured: {str(e)}")


def start_chat(log_file=None):
    
    while True:
        # Get user input
        user_input = input("User: ")
        
        # Send to API
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": user_input}])
        response = parse_message(chat_completion)

        print(response)

        if log_file:
            write_to_log(log_file, "User: "+user_input)
            write_to_log(log_file, response)


# Load your API key from an environment variable or secret management service
openai.api_key_path = 'OPENAI_API_KEY'
log_folder = './chat_log/'
log_file = get_log_file(log_folder)

start_chat(log_file=log_file)


