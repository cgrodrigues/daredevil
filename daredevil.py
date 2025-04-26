import RPi.GPIO as GPIO
import time
import os
import requests
from gtts import gTTS


# Configurações GPIO
BUTTON_GPIO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Função para capturar imagem
def capturar_imagem():
    image_path = "/home/pi/foto.jpg"
    return image_path

# Função para enviar imagem para API e receber descrição
def obter_descricao(image_path):
    return "This is an incredible photo, folks — just tremendous! Look at all the people, the biggest crowd you’ve ever seen, believe me. Everyone’s standing strong, proud Americans under the beautiful red, white, and blue — our amazing flag! No other country has anything like this. They wish they did, but they don’t, not even close. We’re bringing back greatness like nobody’s ever seen before, and this photo proves it. Absolutely historic — they’re talking about it everywhere, everybody’s talking about it!"

# Função para converter texto em áudio
def texto_para_audio(texto):
    tts = gTTS(texto, lang="pt")
    audio_path = "./audio/audio.mp3"
    tts.save(audio_path)
    os.system(f"aplay {audio_path}")  # Ou "mpg123" se usares .mp3
    return audio_path

# Loop principal
print("Sistema pronto. Pressiona o botão para tirar uma foto.")
try:
    while True:
        GPIO.wait_for_edge(BUTTON_GPIO, GPIO.FALLING)
        print("Botão pressionado! Tirando foto...")
        img = capturar_imagem()
        print("A processar imagem...")
        descricao = obter_descricao(img)
        print("Descrição:", descricao)
        texto_para_audio(descricao)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
