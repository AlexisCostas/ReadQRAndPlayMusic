import cv2
from pyzbar.pyzbar import decode
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import re
import warnings

def obtener_uri_cancion(enlace_cancion):
    # Definir la expresión regular
    patron = r'\/([^\/]+)\?'

    uri = 'spotify:track:'

    # Buscar el patrón en la URL
    resultado = re.search(patron, enlace_cancion)

    # Verificar si se encontró el patrón y obtener el resultado
    if resultado:
        uri += resultado.group(1)
        print(uri)
        return uri
    else:
        print("No se encontró el patrón en la URL.")
        return None

def reproducir_cancion_en_spotify(uri_cancion):
    SPOTIPY_CLIENT_ID = '46a42105b2a94e4f9e73a9e5892aa3c1'
    SPOTIPY_CLIENT_SECRET = 'c399c778011f4bc7b914ef39dbfdf604'
    SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

    # Configura la autenticación
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope="user-library-read user-read-playback-state user-modify-playback-state"))

    # Obtiene la lista de dispositivos disponibles
    devices = sp.devices()

    # Verifica si hay dispositivos activos
    if not devices['devices']:
        print("No hay dispositivos activos. Abre la aplicación de Spotify y selecciona un dispositivo.")
        return

    # Reproduce la canción por URI
    sp.start_playback(uris=[uri_cancion])

    return sp

def obtener_genero_artista(sp, artista_id):
    # Obtiene información del artista
    artista = sp.artist(artista_id)

    # Retorna los géneros del artista (puedes ajustar esto según tus necesidades)
    return artista['genres'] if 'genres' in artista else None

def obtener_genero_cancion(sp, uri_cancion):
    # Obtiene información detallada sobre la pista
    track_info = sp.track(uri_cancion)

    # Obtiene el primer artista de la lista de artistas de la canción
    primer_artista_id = track_info['artists'][0]['id']

    # Obtiene el género del primer artista
    genero_artista = obtener_genero_artista(sp, primer_artista_id)

    return genero_artista

def obtener_metadatos_cancion(uri_cancion):
    SPOTIPY_CLIENT_ID = '46a42105b2a94e4f9e73a9e5892aa3c1'
    SPOTIPY_CLIENT_SECRET = 'c399c778011f4bc7b914ef39dbfdf604'
    SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

    # Configura la autenticación
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope="user-library-read user-read-playback-state user-modify-playback-state"))

    # Obtiene información detallada sobre la pista
    track_info = sp.track(uri_cancion)

    # Retorna los metadatos de la pista (puedes ajustar esto según tus necesidades)
    return {
        'nombre': track_info['name'],
        'artistas': [artista['name'] for artista in track_info['artists']],
        'album': track_info['album']['name'],
        'genero': track_info['genres'] if 'genres' in track_info else None  # Aquí deberías obtener el género de otra manera
    }

def leer_codigo_qr_camara():
    cap = cv2.VideoCapture(0)  # 0 para la cámara predeterminada

    while True:
        ret, frame = cap.read()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

        try:

            # Decodifica códigos QR en el fotograma
            codigos_qr = decode(frame)

            for codigo_qr in codigos_qr:
                rect_points = codigo_qr.polygon
                if len(rect_points) == 4:
                    rect_points = [(int(point.x), int(point.y)) for point in rect_points]

                    # Asegúrate de que rect_points contiene coordenadas enteras y es de longitud 4
                    if all(isinstance(coord, int) for point in rect_points for coord in point) and len(rect_points) == 4:
                        rect_points = [(point[0], point[1]) for point in rect_points]

                        # Convierte a numpy array para usar con fillPoly
                        rect_points_np = np.array([rect_points], dtype=np.int32)

                        # Dibuja el polígono
                        cv2.fillPoly(frame, rect_points_np, color=(0, 255, 0))

                        enlace_cancion = codigo_qr.data.decode('utf-8')
                        print("Enlace de la canción:", enlace_cancion)

                        # Obtén el URI de la canción desde el enlace
                        uri_cancion = obtener_uri_cancion(enlace_cancion)

                        if(uri_cancion != None):
                            try:
                                # Reproduce la canción en Spotify
                                sp = reproducir_cancion_en_spotify(uri_cancion)
                                meta_datos = obtener_genero_cancion(sp, uri_cancion)
                                print(meta_datos)
                            except:
                                print("No se encontro la canción en Spotify")
        except Exception as e:
            print(f"Error al decodificar códigos QR: {e}")

        # Muestra el fotograma
        cv2.imshow('QR Scanner', frame)

        # Sal del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera los recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    leer_codigo_qr_camara()
