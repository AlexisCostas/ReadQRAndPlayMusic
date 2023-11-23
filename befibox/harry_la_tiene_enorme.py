import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
import time
from pytube import YouTube
from moviepy.editor import *
from pydub import AudioSegment
from pydub.playback import play
import os
import vlc 
import RPi.GPIO as GPIO
from time import sleep
import time
import re
from googleapiclient.discovery import build
import requests
import pygame

def arranque():
    GPIO.setmode (GPIO.BOARD)
    GPIO.setup (15,GPIO.OUT)
    GPIO.setup (16,GPIO.OUT)
    GPIO.setup (11,GPIO.OUT)
    GPIO.setup (13,GPIO.OUT)

def liberar_recursos(inicio = True):
    GPIO.output(11,False)
    GPIO.output(13,False)
    GPIO.output(16,False)
    GPIO.output(15,False)
    if (inicio == False):
        GPIO.cleanup()

def forward(tiempo = 2):
    GPIO.output(11,GPIO.LOW)
    GPIO.output(13,GPIO.HIGH)
    GPIO.output(16,GPIO.HIGH)
    GPIO.output(15,GPIO.LOW)
    time.sleep(tiempo)
    liberar_recursos()

def reverse(tiempo = 2):
    GPIO.output(11,GPIO.HIGH)
    GPIO.output(13,GPIO.LOW)
    GPIO.output(16,GPIO.LOW)
    GPIO.output(15,GPIO.HIGH)
    time.sleep(tiempo)
    liberar_recursos()

def turn_left(tiempo = 1):
    GPIO.output(11,GPIO.LOW)
    GPIO.output(13,GPIO.HIGH)
    GPIO.output(16,False)
    GPIO.output(15,False)
    time.sleep(tiempo)
    liberar_recursos()

def turn_right(tiempo = 1):
    GPIO.output(11,False)
    GPIO.output(13,False)
    GPIO.output(16,GPIO.HIGH)
    GPIO.output(15,GPIO.LOW)
    time.sleep(tiempo)
    liberar_recursos()

def limpiar_texto(texto):
    # Eliminar caracteres especiales
    texto_limpio = re.sub(r'[^a-zA-Z0-9\s]', '', texto)

    # Eliminar contenido entre corchetes, paréntesis o llaves
    texto_limpio = re.sub(r'\[.?\]|\(.?\)|\{.*?\}', '', texto)

    # Eliminar palabras comunes y específicas
    palabras_a_eliminar = ['official', 'video', 'lyrics', 'live']
    for palabra in palabras_a_eliminar:
        texto_limpio = texto_limpio.replace(palabra, '')

    # Eliminar la cadena "- topic"
    texto_limpio = texto_limpio.replace('- topic', '')

    return texto_limpio.strip()

def obtener_info_youtube(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    print(video_id)
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )

    response = request.execute()

    try:
        item = response['items'][0]
        snippet = item['snippet']
        artist = limpiar_texto(snippet['channelTitle'].lower())
        track = limpiar_texto(snippet['title'].lower())
        return artist, track
    except (KeyError, IndexError):
        return None, None

def obtener_genero_lastfm(artist, track, api_key):
    url = f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={artist}&track={track}&format=json'
    response = requests.get(url)
    data = response.json()

    # Extraer información sobre el género
    try:
        genero = data['track']['toptags']['tag'][0]['name']
        return genero
    except (KeyError, IndexError):
        return None

def do_movement(genre):
    if 'Reggaeton' in genre:
        print('1')
        print(genre)
        reverse(0.5)
        turn_left(0.5)
        turn_right(0.5)
        reverse(0.5)
        turn_left(0.5)
        turn_right(0.5)
        reverse(0.5)
        turn_left(0.5)
        turn_right(0.5)
        reverse(0.5)
        turn_left(0.5)
        turn_right(0.5)
    elif 'jazz' in genre:
        print('2')
        print(genre)
        forward(0.5)
        turn_right(2)
        forward(0.5)
        turn_left(2)
        reverse(0.5)
        turn_right(2)
        reverse(0.5)
        turn_left(2)
    elif 'pop' in genre:
        print('3')
        print(genre)
        turn_right(4)
        turn_left(4)
    elif 'Rock' in genre:
        print('4')
        print(genre)
        forward(0.3)
        reverse(0.3)
        forward(0.3)
        reverse(0.3)
        forward(0.3)
        reverse(0.3)
        forward(0.3)
        reverse(0.3)
    else:
        print(genre)
        print('5')
        forward(0.5)
        turn_right(4)
        reverse(0.5)
        turn_left(4)

def get_genre(url):
    useless, video_id = url.split('=')
    artista, cancion = obtener_info_youtube(api_key_youtube, video_id)
    print(f"Artista: {artista}")
    print(f"Canción: {cancion}")

    genero = obtener_genero_lastfm(artista, cancion, api_key_lastfm)

    if video_id and genero:
        print('El genero es: ' + genero)
        return genero
    else:
        print('No se encontro el genero')
        return 'default'

def download_and_play_youtube_audio(url):
    # Download YouTube video
    genre = get_genre(url)
    yt = YouTube(url)
    ys = yt.streams.filter(only_audio=True).first()
    # Create a sanitized filename
    filename = limpiar_texto(yt.title + ".webm")

    print("Downloading audio...")
    ys.download(filename)
    realfilename= filename+"/"+yt.title+".mp4"

    os.rename(realfilename, limpiar_texto(realfilename))
    # creating vlc media player object 
    media = vlc.MediaPlayer(limpiar_texto(realfilename)) 
    # start playing video 
    media.play() 

    counter = 6
    while (counter > 0):
        do_movement(genre)
        counter = counter - 1
    media.stop()

def reproducir_notificacion():
    pygame.mixer.music.load("notificacion.mp3")
    pygame.mixer.music.play()

api_key_lastfm = '9b602a4f9f1dbc7477d9b7763841c86f'
api_key_youtube = 'AIzaSyB3ORTBf20xS0bDAatM3cv7EU8DyLLPSP8'
MAX_NOT_SEEN = 10
codes = dict()
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
cap = cv2.VideoCapture(0)

pygame.mixer.init()
arranque()
liberar_recursos(True)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    d = decode(gray)

    data = [x.data.decode('utf-8') for x in d]
    bbox = [[[-p.x, p.y] for p in x.polygon] for x in d]

    # Create or update code
    for i, d in enumerate(data):
        if d == '':
            continue

        if d not in codes:
            if d.startswith('https://www.youtube.com') or d.startswith('https://youtu.be'):
                print('El codigo es: ' + d)
                reproducir_notificacion()
                download_and_play_youtube_audio(d)
            else:
                print('Unknown type of QR code')
                print(d)
        else:
            codes[d].update(bbox[i])

    # Get rid of removed codes
    for d in list(codes):
        if d not in data:
            codes[d].not_seen_cnt += 1
            if codes[d].not_seen_cnt > MAX_NOT_SEEN:
                print('Lost %s' % d)
                del codes[d]
        else:
            codes[d].not_seen_cnt = 0

    cv2.imshow("QR Code Reader", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
liberar_recursos(False)