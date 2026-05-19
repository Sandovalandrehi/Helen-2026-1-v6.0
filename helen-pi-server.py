import sys, ssl, numpy as np, json, time, threading, urllib.request
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import mediapipe as mp
from picamera2 import Picamera2
import socketio as sio_client

VPS_URL = 'https://helen.softint.com.mx'

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                       min_detection_confidence=0.5, model_complexity=0)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

vps = sio_client.Client(reconnection=True, reconnection_attempts=0,
                         reconnection_delay=3, logger=False, engineio_logger=False,
                         ssl_verify=False)

def connect_to_vps():
    while True:
        try:
            print('Conectando al VPS...')
            vps.connect(VPS_URL, transports=['polling'])
            vps.wait()
        except Exception as e:
            print(f'VPS desconectado: {e}')
        time.sleep(5)

@vps.on('prediction')
def on_vps_prediction(data):
    gesture = data.get('gesture', 'unknown')
    confidence = data.get('confidence', 0)
    print(f'Gesto: {gesture} ({confidence*100:.1f}%)')
    socketio.emit('prediction', {'gesture': gesture, 'confidence': confidence})

@vps.on('connect')
def on_vps_connect():
    print('Conectado al VPS')

@vps.on('disconnect')
def on_vps_disconnect():
    print('Desconectado del VPS')

def extract_landmarks(frame):
    res = hands.process(frame)
    if not res.multi_hand_landmarks:
        return None
    left, right = np.zeros(63, np.float32), np.zeros(63, np.float32)
    labels = [h.classification[0].label.lower() for h in (res.multi_handedness or [])]
    for i, lm in enumerate(res.multi_hand_landmarks):
        pts = np.array([[p.x, p.y, p.z] for p in lm.landmark], np.float32).flatten()
        label = labels[i] if i < len(labels) else ''
        if 'left' in label:
            left = pts
        elif 'right' in label:
            right = pts
        elif np.all(left == 0):
            left = pts
        else:
            right = pts
    return np.concatenate([left, right])

def camera_loop():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (320, 240)})
    picam2.configure(config)
    picam2.start()
    time.sleep(1)
    print('Camara iniciada (picamera2)')
    frame_count = 0
    while True:
        frame = picam2.capture_array()
        frame_count += 1
        lm = extract_landmarks(frame)
        if frame_count % 100 == 0:
            print(f'Frames: {frame_count}, mano: {lm is not None}, vps: {vps.connected}')
        if lm is not None and vps.connected:
            vps.emit('add_frame', {'landmarks': lm.tolist()})
        time.sleep(0.15)

@app.route('/tapo/state')
def tapo_state():
    try:
        with urllib.request.urlopen('http://127.0.0.1:5002/tapo/state', timeout=5) as r:
            return jsonify(json.loads(r.read()))
    except:
        return jsonify({'state': 'unknown', 'state2': 'unknown'})

@app.route('/tapo/on', methods=['POST'])
def tapo_on():
    try:
        req = urllib.request.Request('http://127.0.0.1:5002/tapo/on', method='POST')
        with urllib.request.urlopen(req, timeout=5) as r:
            return jsonify(json.loads(r.read()))
    except:
        return jsonify({'success': False, 'state': 'unknown'})

@app.route('/tapo/off', methods=['POST'])
def tapo_off():
    try:
        req = urllib.request.Request('http://127.0.0.1:5002/tapo/off', method='POST')
        with urllib.request.urlopen(req, timeout=5) as r:
            return jsonify(json.loads(r.read()))
    except:
        return jsonify({'success': False, 'state': 'unknown'})

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@socketio.on('connect')
def on_browser_connect():
    print('Browser conectado')

if __name__ == '__main__':
    print('Iniciando Helen Pi Server puerto 5001...')
    threading.Thread(target=connect_to_vps, daemon=True).start()
    threading.Thread(target=camera_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
