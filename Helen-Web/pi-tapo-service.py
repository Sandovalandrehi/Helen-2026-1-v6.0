"""
Helen Foco RGB — Tapo/Tuya Service con Auto-Discovery
=====================================================
Maneja focos RGB Tuya con descubrimiento automático de IP.

Flujo de inicio:
  1. Lee device_id, local_key, IP de .env
  2. Prueba la IP guardada (1 intento, timeout 2s)
  3. Si falla → escanea el subnet /24 en paralelo (~3-5s)
  4. Si encuentra → actualiza .env con la nueva IP
  5. Si no encuentra → queda en estado 'unknown' hasta el siguiente comando

Funciona en hotspot (no depende de UDP broadcast, usa TCP directo al puerto 6668).
"""

import os
import re
import socket
import logging
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import tinytuya

logger = logging.getLogger(__name__)

# Ruta del .env (mismo directorio que este archivo)
ENV_PATH = Path(__file__).parent / '.env'


# ── Helpers de red ────────────────────────────────────────────────────────────

def get_local_subnet():
    """Devuelve el prefijo /24 del subnet local (ej: '10.142.244')."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return '.'.join(local_ip.split('.')[:3])
    except Exception as e:
        logger.warning(f"No se pudo determinar subnet local: {e}")
        return None


def _tcp_open(ip, port=6668, timeout=1.0):
    """Devuelve True si el puerto TCP está abierto en esa IP."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def _probe_ip(device_id, local_key, ip, version, timeout=2):
    """
    Verifica primero con TCP si hay algo en el puerto 6668, luego confirma
    con el protocolo Tuya. Devuelve la IP si es el dispositivo correcto.
    """
    if not _tcp_open(ip, timeout=timeout):
        return None
    try:
        d = tinytuya.BulbDevice(device_id, ip, local_key, version=version)
        d.set_socketPersistent(False)
        d.set_socketTimeout(timeout)
        status = d.status()
        # Aceptar cualquier respuesta válida (con o sin dps)
        if isinstance(status, dict) and 'Error' not in status:
            return ip
    except Exception:
        pass
    return None


def discover_device_ip(device_id, local_key, version, subnet=None, max_workers=100):
    """
    Fase 1: TCP scan rápido al puerto 6668 en todo el /24.
    Fase 2: Confirma con protocolo Tuya solo en IPs que respondieron.
    """
    if not subnet:
        subnet = get_local_subnet()
    if not subnet:
        return None

    logger.info(f"Escaneando {subnet}.0/24 para device {device_id[:8]}...")

    # Fase 1 — TCP port scan (rápido, ~2-3s)
    candidates = []
    stop_event = threading.Event()

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_tcp_open, f"{subnet}.{i}", 6668, 1.0): i for i in range(1, 255)}
        for future in as_completed(futures):
            if future.result():
                ip = f"{subnet}.{futures[future]}"
                candidates.append(ip)

    logger.info(f"  Puertos 6668 abiertos: {candidates or 'ninguno'}")

    # Fase 2 — Confirmar device_id con protocolo Tuya
    for ip in candidates:
        if _probe_ip(device_id, local_key, ip, version, timeout=2):
            logger.info(f"  ✅ Device {device_id[:8]} confirmado en {ip}")
            return ip

    logger.warning(f"  ❌ Device {device_id[:8]} no encontrado en el subnet")
    return None


def update_env_ip(env_var_name, new_ip, env_path=ENV_PATH):
    """Actualiza la variable IP en el archivo .env (preserva el resto)."""
    try:
        if not env_path.exists():
            return False
        content = env_path.read_text()
        pattern = rf'^{env_var_name}=.*$'
        if re.search(pattern, content, flags=re.MULTILINE):
            new_content = re.sub(pattern, f'{env_var_name}={new_ip}',
                                  content, flags=re.MULTILINE)
        else:
            new_content = content.rstrip() + f'\n{env_var_name}={new_ip}\n'
        env_path.write_text(new_content)
        logger.info(f"  💾 {env_var_name}={new_ip} guardado en .env")
        return True
    except Exception as e:
        logger.error(f"Error guardando {env_var_name} en .env: {e}")
        return False


# ── Servicio principal ────────────────────────────────────────────────────────

class BulbService:
    _DP_SWITCH = "20"

    def __init__(self,
                 device_id_env="TUYA_DEVICE_ID",
                 local_key_env="TUYA_LOCAL_KEY",
                 ip_env="TUYA_IP",
                 version_env="TUYA_VERSION"):

        self._device_id = os.getenv(device_id_env, "").strip()
        self._local_key = os.getenv(local_key_env, "").strip()
        self._ip = os.getenv(ip_env, "").strip()
        self._version = float(os.getenv(version_env, "3.5"))
        self._ip_env_name = ip_env
        self._device_label = device_id_env

        self.current_state = 'unknown'
        self._lock = threading.Lock()

        if not self._device_id or not self._local_key:
            logger.warning(f"{device_id_env}: credenciales incompletas, deshabilitado")
            self.is_enabled = False
            return

        self.is_enabled = True

        # Probar IP configurada; si falla, escanear
        if self._ip and _probe_ip(self._device_id, self._local_key, self._ip, self._version):
            logger.info(f"{device_id_env}: IP {self._ip} respondiendo ✅")
        else:
            if self._ip:
                logger.info(f"{device_id_env}: IP {self._ip} no responde, escaneando...")
            else:
                logger.info(f"{device_id_env}: sin IP configurada, escaneando...")

            found_ip = discover_device_ip(self._device_id, self._local_key, self._version)
            if found_ip:
                self._ip = found_ip
                update_env_ip(ip_env, found_ip)
            else:
                logger.warning(f"{device_id_env}: dispositivo no encontrado en la red")

    # ── Conexión interna ──────────────────────────────────────────────────────

    def _get_device(self):
        if not self.is_enabled or not self._ip:
            return None
        try:
            d = tinytuya.BulbDevice(self._device_id, self._ip,
                                    self._local_key, version=self._version)
            d.set_socketPersistent(False)
            d.set_socketTimeout(3)
            return d
        except Exception as e:
            logger.error(f"{self._device_label}: error creando device: {e}")
            return None

    def _rediscover(self):
        """Re-escanea el subnet (cuando una operación falla por IP cambiada)."""
        logger.info(f"{self._device_label}: re-descubriendo IP...")
        found_ip = discover_device_ip(self._device_id, self._local_key, self._version)
        if found_ip and found_ip != self._ip:
            self._ip = found_ip
            update_env_ip(self._ip_env_name, found_ip)
            return True
        return False

    # ── API pública ───────────────────────────────────────────────────────────

    def get_state(self):
        """Consulta en vivo el estado del foco. Si falla, intenta re-discover."""
        if not self.is_enabled:
            return 'unknown'
        with self._lock:
            # Si no hay IP (no se encontro al inicio), intentar descubrir con rate limit
            if not self._ip:
                import time as _t
                now = _t.time()
                last_try = getattr(self, '_last_discover_try', 0)
                if now - last_try > 30:  # reintentar como max cada 30s
                    self._last_discover_try = now
                    logger.info(f"{self._device_label}: sin IP, reintentando descubrir...")
                    self._rediscover()

            d = self._get_device()
            if not d:
                self.current_state = 'unknown'
                return 'unknown'
            try:
                status = d.status()
                dps = status.get('dps', {}) if isinstance(status, dict) else {}
                if self._DP_SWITCH in dps:
                    self.current_state = 'on' if dps[self._DP_SWITCH] else 'off'
                    return self.current_state
            except Exception as e:
                logger.warning(f"{self._device_label}: status falló ({e}), re-discover")
                if self._rediscover():
                    return self.get_state()  # reintentar con la nueva IP
            self.current_state = 'unknown'
            return 'unknown'

    def turn_on(self):
        return self._set_switch(True)

    def turn_off(self):
        return self._set_switch(False)

    def _set_switch(self, on):
        if not self.is_enabled:
            return False
        with self._lock:
            d = self._get_device()
            if not d:
                return False
            try:
                d.set_status(on, 20)
                self.current_state = 'on' if on else 'off'
                return True
            except Exception as e:
                logger.warning(f"{self._device_label}: set_status falló ({e}), re-discover")
                if self._rediscover():
                    d2 = self._get_device()
                    if d2:
                        try:
                            d2.set_status(on, 20)
                            self.current_state = 'on' if on else 'off'
                            return True
                        except Exception:
                            pass
            return False


# ── Instancias globales ───────────────────────────────────────────────────────

tapo_service = BulbService(
    "TUYA_DEVICE_ID", "TUYA_LOCAL_KEY", "TUYA_IP", "TUYA_VERSION"
)

tapo_service2 = BulbService(
    "TUYA_DEVICE_ID_2", "TUYA_LOCAL_KEY_2", "TUYA_IP_2", "TUYA_VERSION_2"
)
