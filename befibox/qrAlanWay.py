import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
import math
import fluidsynth
import threading
import time
import alsaaudio
import webbrowser
from pytube import YouTube
from moviepy.editor import *
from pydub import AudioSegment
from pydub.playback import play
import os
import vlc 

def sanitize_filename(title):
    valid_chars = '-_()[]{}.,;'

    title_without_spaces = ''.join(c if c.isalnum() or c in valid_chars else '_' for c in title)

    return title_without_spaces

def download_and_play_youtube_audio(url):
    # Download YouTube video
    yt = YouTube(url)
    ys = yt.streams.filter(only_audio=True).first()
    # Create a sanitized filename
    filename = sanitize_filename(yt.title + ".webm")
    
    print("Downloading audio...")
    ys.download(filename)
    realfilename= filename+"/"+yt.title+".mp4"

    # creating vlc media player object 
    media = vlc.MediaPlayer(realfilename) 
    
    # start playing video 
    media.play() 
    
    print("el codigo sigue ejecutandose")
    # try:
    #     # Print file information
    #     os.startfile(realfilename)
    #     print("File Info:")
    os.system(f"ffprobe -v error -show_format -show_streams {realfilename}")
    #     # # Convert video to audio using moviepy
    #     # audio_clip = AudioFileClip(realfilename, 0)
    #     # audio_clip.preview()
    #     print("Playing audio...")

    # except Exception as e:
    #     print(f"Error processing the video: {e}")

    

codes = dict()
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
cap = cv2.VideoCapture(0)

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