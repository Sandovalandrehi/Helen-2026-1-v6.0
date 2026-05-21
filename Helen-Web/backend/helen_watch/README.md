# helen_watch

Módulo de integración del reloj **Helen-ESP32** con el backend de Helen.

## Qué hace

Expone dos endpoints HTTP que el firmware del reloj consume:

| Endpoint | Método | Para qué |
|----------|--------|----------|
| `/external_gesture` | POST | El reloj reporta un gesto detectado localmente → backend re-emite el evento Socket.IO `prediction` al frontend (mismo formato que `predict_gesture()` del server principal). |
| `/watch_summary?cmd=...` | GET | El reloj pide un resumen pequeño (clima, alarmas) para mostrar en su LCD. Por ahora devuelve placeholders. |

## Diseño

- **Aditivo, no invasivo.** El módulo se registra como Flask Blueprint vía `register(app, socketio)`.
- Reutiliza el `socketio` del `server.py` principal para emitir el evento `prediction`. El frontend no se entera de que viene del reloj.
- **No toca** `ml-service/`, `tapo_service.py`, ni la lógica de cámara/LSTM.
- Carga su propia copia de `gestures_map.json` (lectura solamente) para validar comandos, sin compartir estado mutable con `server.py`.

## Cómo se conecta a server.py

En `server.py` se agregan **dos líneas** (siguen el patrón existente de `sys.path.insert` para `ml-service`):

```python
sys.path.insert(0, str(Path(__file__).parent.parent))
from helen_watch import register; register(app, socketio)
```

Si se quitan esas dos líneas, el módulo queda inerte y Helen funciona idéntico a antes del cambio.

## Pruebas rápidas

```bash
# Simular gesto del reloj
curl -X POST http://localhost:5001/external_gesture \
  -H "Content-Type: application/json" \
  -d '{"gesture":"home","confidence":0.95}'
# → 200 {"status":"ok"} y el frontend navega a Home

# Pedir resumen para el LCD
curl http://localhost:5001/watch_summary?cmd=clima
# → 200 {"icon":"sun","temp_c":22,"city":"Tijuana"}

# Gesto desconocido
curl -X POST http://localhost:5001/external_gesture \
  -H "Content-Type: application/json" \
  -d '{"gesture":"inventado","confidence":0.5}'
# → 400 {"error":"unknown gesture: inventado"}
```

## Autenticación opcional

Si en el backend se define la env var `HELEN_EXTERNAL_TOKEN`, el reloj debe
enviar el header `X-Helen-Token: <mismo valor>` en cada POST a
`/external_gesture`, o recibirá 401. Recomendado para deploy en VPS/cloud.

## Pendientes (post-MVP)

- Cablear `_placeholder_weather()` a la fuente real de clima (OpenWeather).
- Cablear `_placeholder_alarms()` al storage de alarmas cuando se persistan en el backend.
