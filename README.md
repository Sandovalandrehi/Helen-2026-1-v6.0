# Helen-2026-1-v6.0

Sistema Helen v6.0 - Plataforma de control para personas con discapacidad auditiva mediante reconocimiento de gestos.

## Componentes

### Backend
- **Helen-Web/backend/ml-service**: Servicio de Machine Learning para reconocimiento de gestos (PyTorch + MediaPipe).
- **Helen-Web/backend/websocket-server**: Servidor WebSocket que recibe landmarks y emite predicciones.

### Frontend
- **Helen-Web/frontend/web-app**: Aplicacion web React (Vite) con navegacion por gestos.

### Servicios Raspberry Pi
- **helen-pi-server.py**: Captura camara con picamera2 + MediaPipe, envia landmarks al VPS via Socket.IO, recibe predicciones y las reenvia al browser.
- **Helen_startup.sh**: Script de arranque automatico en modo kiosk.
- **pi-foco-server.py / tapo_service.py**: Servicio local para control de focos RGB via protocolo Tuya.

### Utilidades
- **grabarVideo.py**: Captura de videos para el dataset de entrenamiento.
- **merge_gestures.py**: Combina datasets de varias personas en la estructura esperada por data_prep.py.
- **upload_*.py**: Scripts para subir archivos al VPS via SFTP.

## Arquitectura

```
Pi (camera + MediaPipe)
  -> landmarks via Socket.IO
  -> VPS (PyTorch inference)
  -> prediction via Socket.IO
  -> Pi (browser)
  -> Helen UI navegacion

Pi (helen-foco)
  -> tinytuya
  -> Focos RGB (red local)
```

## Setup

Ver `GUIA-GRABACION-GESTOS.md` para capturar datos de entrenamiento.
Ver `CONSENTIMIENTO-GRABACION.md` para el formato de consentimiento.

## Notas

- Las credenciales (.env, tinytuya.json) NO se suben al repositorio.
- Los videos del dataset y los archivos entrenados (.npy, .pth) se generan localmente.
