import re
from googleapiclient.discovery import build
import requests


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


api_key_lastfm = '9b602a4f9f1dbc7477d9b7763841c86f'
api_key_youtube = 'AIzaSyB3ORTBf20xS0bDAatM3cv7EU8DyLLPSP8'
video_id = 'YR2CMfQoa08'

artista, cancion = obtener_info_youtube(api_key_youtube, video_id)

if artista and cancion:
    print(f"Artista: {artista}")
    print(f"Canción: {cancion}")

    genero = obtener_genero_lastfm(artista, cancion, api_key_lastfm)

    if genero:
        print(f"El género de la canción es: {genero}")
    else:
        print("No se pudo obtener información sobre el género.")
else:
    print("No se pudo obtener información sobre el video de YouTube.")