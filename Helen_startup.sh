#!/bin/bash
###############################################################################
# Helen - Raspberry Pi 5 Kiosk Mode Startup Script (Bulletproof)
###############################################################################

LOG="/tmp/helen_startup.log"
LOCK="/tmp/helen_startup.lock"
exec >> "$LOG" 2>&1

# Prevenir ejecucion duplicada (autostart + lxsession lo llaman 2 veces)
if [ -f "$LOCK" ]; then
    LOCK_PID=$(cat "$LOCK" 2>/dev/null)
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        echo "$(date) - Ya hay una instancia corriendo (PID $LOCK_PID), saliendo"
        exit 0
    fi
fi
echo $$ > "$LOCK"

# Cleanup del lock al salir
trap "rm -f $LOCK" EXIT

echo ""
echo "============================================================"
echo "$(date) - Iniciando Helen (PID $$)"
echo "============================================================"

# Esperar red (max 60 segundos)
echo "Esperando conexion de red..."
for i in {1..60}; do
    if ping -c 1 -W 1 8.8.8.8 &>/dev/null; then
        echo "Red disponible"
        break
    fi
    sleep 1
done

sleep 3

xset s off
xset -dpms
xset s noblank

unclutter -idle 0.5 -root &

# Matar lo previo (NO matamos helen-foco porque lo gestiona systemd)
echo "Limpiando procesos previos..."
pkill -9 -f helen-pi-server || true
pkill -9 -f "http.server 8080" || true
fuser -k 5001/tcp 2>/dev/null || true
fuser -k 8080/tcp 2>/dev/null || true
sleep 3

# === Esperar a que focos (systemd) respondan en 5002 ===
echo "Esperando servicio de focos (puerto 5002 via systemd)..."
for i in {1..30}; do
    if curl -s --max-time 2 http://localhost:5002/tapo/state &>/dev/null; then
        echo "Focos OK en puerto 5002"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ADVERTENCIA: Focos no respondieron en 30s"
    fi
    sleep 1
done

# === Iniciar Helen Pi Server en puerto 5001 ===
echo "Iniciando Helen Pi Server (puerto 5001)..."
cd /home/helen/Desktop/Helen/backend
source ml-service/venv/bin/activate
nice -n 15 nohup python helen-pi-server.py > /tmp/helen.log 2>&1 &
PI_PID=$!
echo "Helen Pi Server PID: $PI_PID"

# Esperar a que helen-pi-server responda (max 30s)
for i in {1..30}; do
    if curl -s --max-time 2 http://localhost:5001/health &>/dev/null; then
        echo "Helen Pi Server OK en puerto 5001"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ADVERTENCIA: Helen Pi Server no respondio en 30s"
    fi
    sleep 1
done

# === Servidor HTTP del frontend en puerto 8080 ===
echo "Iniciando servidor HTTP (puerto 8080)..."
nohup python3 -m http.server 8080 --directory /home/helen/helen-local > /tmp/http8080.log 2>&1 &
HTTP_PID=$!
echo "HTTP PID: $HTTP_PID"

# Esperar HTTP server
for i in {1..15}; do
    if curl -s --max-time 2 http://localhost:8080/ &>/dev/null; then
        echo "HTTP server OK"
        break
    fi
    sleep 1
done

# === Verificar estado final ===
echo ""
echo "===== Estado final ====="
ss -tlnp 2>/dev/null | grep -E "5001|5002|8080" || echo "Algun puerto no esta escuchando"
echo "========================="

# Abrir Chromium en kiosk
echo "Iniciando Chromium..."
chromium-browser \
  --noerrdialogs \
  --disable-infobars \
  --disable-features=TranslateUI \
  --disable-suggestions-service \
  --disable-save-password-bubble \
  --disable-session-crashed-bubble \
  --start-fullscreen \
  --kiosk \
  --allow-insecure-localhost \
  --use-fake-ui-for-media-stream \
  --autoplay-policy=no-user-gesture-required \
  http://localhost:8080 &

echo "$(date) - Helen iniciado correctamente"
