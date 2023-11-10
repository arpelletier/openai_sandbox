import os
import openai
import requests
from PIL import Image
from io import BytesIO
import sys
import datetime

sys.path.append('../')
from config import OPENAI_KEY


def download_image(url, output='image.png'):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.save(output)

    return output


def image_prompt(prompt, out_dir='.', n=1):
    image_resp = openai.Image.create(prompt=prompt, n=n, size="512x512")
    for i in range(n):
        image_url = image_resp['data'][i]['url']
        out_img = os.path.join(out_dir, 'image_%d.png' % i)
        download_image(image_url, output=out_img)


def user_image_prompt(out_dir='.'):
    # Get user prompt
    prompt = input("Enter a prompt: ")
    replicates = input("Number of images to generate: ")
    try:
        replicates = int(replicates)
    except ValueError:
        print("Invalid input. Defaulting to 1.")
        replicates = 1

    timestamp = get_date_time()
    img_out_dir = os.path.join(out_dir, timestamp+"_image")
    # Make folder for output
    if not os.path.exists(img_out_dir):
        os.makedirs(img_out_dir)

    # Save prompt
    with open(os.path.join(img_out_dir, 'prompt.txt'), 'w') as out_file:
        out_file.write(prompt)

    # Generate images
    image_prompt(prompt, img_out_dir, n=replicates)


def get_user_prompt(options):
    """
    Return a user prompt based on the functionalities.
    """
    prompt = "Please select an option:\n"
    for key, value in options.items():
        prompt += f"{key}: {value[0]}\n"
    return prompt


def get_date_time():
    """
    Return a timestamp for the current date and time.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def interactive():
    interactive_options = {'i': ('image', 'Generate an image using OpenAI API')
                           }
    timestamp = get_date_time()
    out_dir = os.path.join('../output', timestamp+"_session")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    while True:
        # Get user input
        user_input = input(get_user_prompt(interactive_options))

        if user_input == 'i':
            print("Image.")
            user_image_prompt(out_dir=out_dir)


if __name__ == "__main__":
    openai.api_key = OPENAI_KEY
    interactive()
# prompt = 'A chicken crossing the road'
# prompt = 'A view of Night City from Cyberpunk 2077'
