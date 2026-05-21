"""
helen_watch — Módulo de integración del reloj Helen-ESP32 con el backend Helen.

Diseño
------
- Se importa desde server.py vía `from helen_watch import register`.
- La función `register(app, socketio)` registra los endpoints HTTP del reloj
  como Flask Blueprint, reutilizando el Socket.IO del servidor principal
  para emitir el evento 'prediction' al frontend.
- Cero modificaciones a la lógica de cámara/MediaPipe/LSTM/Tapo. Si quitas
  las dos líneas de server.py que importan este módulo, Helen queda igual.

Estructura
----------
- routes.py:        Blueprint con /external_gesture y /watch_summary
- watch_summary.py: Datos placeholder para LCD del reloj (clima, alarmas)
"""

from .routes import register

__all__ = ['register']
