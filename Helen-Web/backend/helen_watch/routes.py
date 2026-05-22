"""
HTTP endpoints para integrar el reloj Helen-ESP32.

POST /external_gesture
    Recibe una detección de gesto del reloj (que hizo inferencia local con
    Edge Impulse y ya tradujo su label a un comando Helen) y re-emite el
    evento Socket.IO 'prediction' con el mismo payload que predict_gesture()
    del server.py oficial. El frontend reacciona idéntico que si la cámara
    hubiera detectado el gesto.

GET /watch_summary?cmd=<home|clima|alarma>
    Devuelve un JSON pequeño que el reloj usa para renderizar su LCD.
    Por ahora son placeholders; el cableo a fuentes reales (API de clima,
    storage de alarmas) es follow-up.
"""

import os
import json
import logging
from pathlib import Path

from flask import Blueprint, request, jsonify

from .watch_summary import build_summary

logger = logging.getLogger(__name__)

###############################################################################
# Blueprint
###############################################################################
bp = Blueprint('helen_watch', __name__)

###############################################################################
# Carga propia de gestures_map.json
#
# Mantener nuestra propia copia (lectura) en lugar de compartir el dict de
# server.py evita acoplamientos con el ciclo de vida de load_model() y deja
# este módulo auto-suficiente.
###############################################################################
_GESTURES_MAP_PATH = Path(__file__).parent.parent / 'ml-service' / 'data' / 'gestures_map.json'
try:
    with open(_GESTURES_MAP_PATH, 'r', encoding='utf-8') as f:
        _gestures_map = json.load(f)
    logger.info(f"[helen_watch] Gestures cargados: {list(_gestures_map.keys())}")
except Exception as exc:
    logger.error(f"[helen_watch] No se pudo cargar gestures_map.json: {exc}")
    _gestures_map = {}

###############################################################################
# Estado inyectado al llamar register()
###############################################################################
_socketio = None


def register(app, socketio):
    """
    Registra el blueprint del reloj en la app Flask del server principal.

    Args:
        app: instancia Flask del server.py
        socketio: instancia Flask-SocketIO del server.py (se usa para emitir
                  el evento 'prediction' al frontend que ya está conectado)
    """
    global _socketio
    _socketio = socketio
    app.register_blueprint(bp)
    logger.info("[helen_watch] Blueprint registrado: POST /external_gesture, GET /watch_summary")


###############################################################################
# Endpoints
###############################################################################
@bp.route('/external_gesture', methods=['POST'])
def external_gesture():
    """
    Recibe un gesto del reloj y re-emite el evento Socket.IO 'prediction'.

    Body JSON esperado:
        gesture (str):      nombre del comando Helen (debe existir en gestures_map.json)
        confidence (float): confianza en [0, 1]
        source (str, opt):  identificador del emisor (ej. "esp32")

    Header opcional:
        X-Helen-Token: secreto compartido. Solo se valida si la env var
                       HELEN_EXTERNAL_TOKEN está presente en el backend.
    """
    data = request.get_json(silent=True) or {}

    # Token primero para no filtrar información sobre el body a un atacante sin token
    expected = os.getenv('HELEN_EXTERNAL_TOKEN')
    if expected and request.headers.get('X-Helen-Token') != expected:
        return jsonify({'error': 'unauthorized'}), 401

    gesture = data.get('gesture')
    confidence = data.get('confidence')

    if gesture not in _gestures_map:
        return jsonify({'error': f'unknown gesture: {gesture}'}), 400
    if (not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
            or not 0.0 <= float(confidence) <= 1.0):
        return jsonify({'error': 'confidence must be a float in [0,1]'}), 400

    payload = {
        'gesture': gesture,
        'gesture_id': _gestures_map[gesture],
        'confidence': float(confidence),
    }

    if _socketio is None:
        logger.error("[helen_watch] socketio no inicializado — register() no se llamó")
        return jsonify({'error': 'helen_watch not initialized'}), 500

    logger.info(f"[helen_watch] Emitting prediction from source={data.get('source')}: {payload}")
    _socketio.emit('prediction', payload, to='watch_clients')
    return jsonify({'status': 'ok'}), 200


@bp.route('/watch_summary', methods=['GET'])
def watch_summary():
    """
    Devuelve un JSON pequeño para que el reloj renderice su LCD después de
    triggear un gesto. Por ahora retorna placeholders.

    Query string:
        cmd: 'home' | 'clima' | 'alarma' (otros valores → {"icon":"none"})
    """
    cmd = request.args.get('cmd', '')
    return jsonify(build_summary(cmd)), 200
