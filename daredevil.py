import time
import os
import requests
from gtts import gTTS

import base64
import io
from groq import Groq
from PIL import Image
from dotenv import load_dotenv

import RPi.GPIO as GPIO
import time

current_path = "/home/admin/daredevil"
model = "meta-llama/llama-4-scout-17b-16e-instruct"
#tld="us"
tld="co.uk"
#tld="co.in"
lang="en"

tld="pt"
lang="pt"

pin = 17

# Função para capturar imagem
def capturar_imagem():
    image_path = f"{current_path}/images/Grand_Canyon_of_yellowstone.jpg"
    return image_path

def encode_image(image_path, image_type="png"):
    """
    Function to encode image inputs to base64 format, which is required by Groq API.

    Args:
        image_path (str): Path to the image file.
        image_type (str): Type of the image file ('png' or 'jpeg').

    Returns:

    """

    supported_types = ["png", "jpeg", "jpg"]
    if image_type.lower() not in supported_types:
        raise ValueError(f"Unsupported image type '{image_type}'. Supported types: {supported_types}")

    # Check if the file exists
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found at path: {image_path}")

    # Open the image
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert("RGB")  # Ensure the image is in RGB format


    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Função para enviar imagem para API e receber descrição
def obter_descricao(image, prompt, api_key, is_url=False):
    """
    Function that will analyze the input image using the llama-3.2 model powered by Groq.
    """
    client = Groq(api_key=api_key)

    if is_url:
        image_content = {"type": "image_url", "image_url": {"url": image}}
    else:
        base64_image = encode_image(image)
        image_content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        image_content,
                    ],
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Função para converter texto em áudio
def texto_para_audio(texto):
    tts = gTTS(texto, lang=lang, tld=tld)
    audio_path = f"{current_path}/audio/audio.mp3"
    tts.save(audio_path)
    #os.system(f"aplay {audio_path}")  # Ou "mpg123" se usares .mp3
    os.system(f"mpg123 {audio_path}")  # Ou "mpg123" se usares .mp3
    return audio_path

# Loop principal
print("Sistema pronto. Pressiona o botão para tirar uma foto.")
try:
    load_dotenv()
    # Usar numeração BCM dos GPIOs
    GPIO.setmode(GPIO.BCM)
    # Configurar o botão como entrada com pull-up
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    api_key = os.environ.get("GROQ_API_KEY")
    prompt = """You are a digital assistant designed to provide visual feedback for blind
individuals, helping them navigate their surroundings. Upon receiving an image, describe
in detail the key objects and structures, including their relative positions and contextual
information. Your responses should be concise, clear, and informative,
enabling users to orient themselves effectively. Additionally, learn and adapt to frequently
visited places to provide personalized guidance. Be natural in your responses, and focus on
providing valuable assistance to empower your users in their daily navigation. Describe the image in European Portuguese."""
    while True:
        if GPIO.input(pin) == GPIO.LOW:
            print(f"Botão pressionado no GPIO {pin}!")
            img = capturar_imagem()
            print("A processar imagem...")
            descricao = obter_descricao(img, prompt, api_key)
            print("Descrição:", descricao)
            texto_para_audio(descricao)
except KeyboardInterrupt:
        print("Error")
finally:
    GPIO.cleanup()
