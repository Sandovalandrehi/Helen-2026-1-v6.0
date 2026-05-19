"""
Helen Foco RGB — Pi Local Service  (puerto 5001)
================================================
Sirve el estado del foco RGB vía REST + Socket.IO en el puerto 5001,
que es el valor por defecto de VITE_WEBSOCKET_URL en el frontend.

Rutas REST:
  GET  /health       → estado general del servicio
  GET  /tapo/state   → estado actual del foco ("on" | "off" | "unknown")
  POST /tapo/on      → encender foco
  POST /tapo/off     → apagar foco

Eventos Socket.IO emitidos:
  tapo_state  →  { state: "on"|"off", success: bool }

Dependencias (ya instaladas en el Pi):
  pip install flask flask-socketio flask-cors python-dotenv tinytuya
"""

import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (mismo directorio)
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── Flask + Socket.IO ─────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

# ── Importar el servicio Tuya (archivo en el mismo directorio) ────────────────
from tapo_service import tapo_service


# ── REST endpoints ────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que el servicio está activo."""
    return {
        'status': 'ok',
        'tapo_state': tapo_service.current_state,
        'tapo_enabled': tapo_service.is_enabled
    }


@app.route('/tapo/state', methods=['GET'])
def tapo_state():
    """Devuelve el estado actual del foco (consulta en vivo)."""
    return {
        'state': tapo_service.get_state(),
        'enabled': tapo_service.is_enabled
    }


@app.route('/tapo/on', methods=['POST'])
def tapo_on():
    """Enciende el foco y notifica a todos los clientes via Socket.IO."""
    success = tapo_service.turn_on()
    state = tapo_service.current_state
    socketio.emit('tapo_state', {'state': state, 'success': success})
    logger.info(f'Foco encendido — state={state} success={success}')
    return {'success': success, 'state': state}


@app.route('/tapo/off', methods=['POST'])
def tapo_off():
    """Apaga el foco y notifica a todos los clientes via Socket.IO."""
    success = tapo_service.turn_off()
    state = tapo_service.current_state
    socketio.emit('tapo_state', {'state': state, 'success': success})
    logger.info(f'Foco apagado — state={state} success={success}')
    return {'success': success, 'state': state}


# ── Socket.IO eventos ─────────────────────────────────────────────────────────

@socketio.on('connect')
def handle_connect():
    logger.info('Cliente conectado via Socket.IO')


@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Cliente desconectado')


# ── Arranque ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('FOCO_PORT', 5001))
    logger.info('=' * 60)
    logger.info(f'Helen Foco RGB Service arrancando en puerto {port}')
    logger.info(f'  GET  http://localhost:{port}/tapo/state')
    logger.info(f'  POST http://localhost:{port}/tapo/on')
    logger.info(f'  POST http://localhost:{port}/tapo/off')
    logger.info('=' * 60)
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
