import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
import math
import fluidsynth
import threading
import time
import mpd
import alsaaudio
import webbrowser

class Code:
    def __init__(self, data, bbox, angle_event_size=3):
        self.data = data
        self.bbox = bbox
        self.not_seen_cnt = 0
        self.angle_offset = 0

        self.initial_angle = self.angle()
        self.last_angle = self.initial_angle
        self.last_angle_event_angle = self.initial_angle
        self.ANGLE_EVENT_SIZE = angle_event_size

    def angle(self):
        vec = [self.bbox[0][0] - self.bbox[1][0], self.bbox[0][1] - self.bbox[1][1]]
        ang = math.atan2(vec[0], vec[1]) * 180 / math.pi - 90 + self.angle_offset
        return ang

    def angle_event(self):
        pass

    def update(self, bbox):
        self.bbox = bbox
        if abs(self.angle() - self.last_angle) >= 45:
            if self.angle() - self.last_angle > 0:
                self.angle_offset -= 90
            else:
                self.angle_offset += 90

        self.last_angle = self.angle()

        if abs(self.last_angle_event_angle - self.angle()) >= self.ANGLE_EVENT_SIZE:
            self.angle_event()
            self.last_angle_event_angle = self.angle()

class SeekCode(Code):
    def __init__(self, data, bbox):
        super().__init__(data, bbox)
        ack_sound()

    def angle_event(self):
        if self.last_angle_event_angle - self.angle() > 0:
            print('Seeking +10s')
            client.seekcur('+10')
        else:
            print('Seeking -10s')
            client.seekcur('-10')

class InstrumentCode(Code):
    def __init__(self, data, bbox):
        super().__init__(data, bbox)
        print(data)

        self.note = 60

    def angle_event(self):
        global fs
        if self.last_angle_event_angle - self.angle() > 0:
            self.note += 1
        else:
            self.note -= 1

        fs.noteon(0, self.note, 127)

class CallBrowser(Code):
    def __init__(self, data, bbox):
        super().__init__(data, bbox)
        webbrowser.open(Code)
        
codes = dict()

cv2.namedWindow("QR Code Reader", cv2.WINDOW_NORMAL)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

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
                codes[d] = CallBrowser(d, bbox[i])            
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
