import openai

from config import OPENAI_KEY
def call_openai_api(user_input):
    try:
        openai.api_key = OPENAI_KEY

        messages = [{"role": "user", "content": user_input}]
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        response = chat_completion['choices'][0]['message']['content']

        return response
    except Exception as e:
        return str(e)


