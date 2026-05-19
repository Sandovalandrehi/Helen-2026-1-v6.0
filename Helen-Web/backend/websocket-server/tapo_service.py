"""
Bulb Service para Helen v5.0 — Foco RGB RadioShack (Tuya)

Controla el foco inteligente via protocolo Tuya local (tinytuya).
No requiere internet: la comunicación es directa en la red local.

Variables de entorno requeridas (.env):
    TUYA_DEVICE_ID  — ID del dispositivo  (ej: ebe997370c6c715b97qsgw)
    TUYA_LOCAL_KEY  — Clave local          (ej: $D1.$H;hB0{+RzbA)
    TUYA_IP         — IP local del foco    (ej: 192.168.1.4)
    TUYA_VERSION    — Versión del protocolo (ej: 3.5)

Data Points del foco (SAA00855-N):
    DP 20  switch_led     Boolean  — encendido/apagado
    DP 21  work_mode      Enum     — 'white' | 'colour' | 'scene' | 'music'
    DP 22  bright_value   Integer  — brillo 10-1000
    DP 23  temp_value     Integer  — temperatura color 0-1000
    DP 24  colour_data    JSON     — color HSV
"""

import os
import logging
import threading

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

###############################################################################
# Import opcional — modo deshabilitado si tinytuya no está instalado
###############################################################################
try:
    import tinytuya
    _TINYTUYA_AVAILABLE = True
except ImportError:
    _TINYTUYA_AVAILABLE = False
    logger.warning("tinytuya no instalado. Control del foco deshabilitado.")


###############################################################################
# BulbService
###############################################################################

class BulbService:
    """
    Controla el foco RGB RadioShack via protocolo Tuya local.

    API pública:
        turn_on()      -> bool   (True = comando enviado OK)
        turn_off()     -> bool
        get_state()    -> 'on' | 'off' | 'unknown'
        is_enabled     -> bool
        current_state  -> 'on' | 'off' | 'unknown'  (caché, sin red)
    """

    # DP del foco que usamos
    _DP_SWITCH = '20'   # switch_led (Boolean)

    def __init__(self):
        self._device_id  = os.getenv('TUYA_DEVICE_ID', '').strip()
        self._local_key  = os.getenv('TUYA_LOCAL_KEY', '').strip()
        self._ip         = os.getenv('TUYA_IP', '').strip()
        self._version    = float(os.getenv('TUYA_VERSION', '3.5'))

        self._bulb  = None       # tinytuya.BulbDevice (lazy)
        self._state = None       # True=on  False=off  None=desconocido
        self._lock  = threading.Lock()

        self._enabled = bool(
            self._device_id and self._local_key
            and self._ip and _TINYTUYA_AVAILABLE
        )

        if self._enabled:
            logger.info(
                f"BulbService listo — IP: {self._ip} "
                f"ID: {self._device_id[:8]}... v{self._version}"
            )
        else:
            razones = []
            if not _TINYTUYA_AVAILABLE:
                razones.append("tinytuya no instalado")
            if not self._device_id:
                razones.append("TUYA_DEVICE_ID faltante")
            if not self._local_key:
                razones.append("TUYA_LOCAL_KEY faltante")
            if not self._ip:
                razones.append("TUYA_IP faltante")
            logger.warning(f"BulbService DESHABILITADO — {', '.join(razones)}")

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _get_bulb(self) -> 'tinytuya.BulbDevice':
        """Devuelve el dispositivo, creándolo si es necesario."""
        if self._bulb is None:
            self._bulb = tinytuya.BulbDevice(
                dev_id=self._device_id,
                address=self._ip,
                local_key=self._local_key,
                version=self._version
            )
            # No mantener socket abierto entre comandos
            self._bulb.set_socketPersistent(False)
            logger.info("BulbService: dispositivo Tuya inicializado")
        return self._bulb

    def _reset(self):
        """Descarta la instancia para forzar reconexión en el próximo comando."""
        self._bulb = None

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @property
    def current_state(self) -> str:
        """Estado en caché — sin llamada de red."""
        if self._state is True:
            return 'on'
        if self._state is False:
            return 'off'
        return 'unknown'

    def turn_on(self) -> bool:
        """
        Enciende el foco.

        Returns:
            True  — comando enviado correctamente.
            False — servicio deshabilitado o error de red.
        """
        if not self._enabled:
            logger.warning("BulbService: turn_on ignorado (deshabilitado)")
            return False

        with self._lock:
            try:
                bulb = self._get_bulb()
                bulb.turn_on()
                self._state = True
                logger.info("Foco RGB → ENCENDIDO")
                return True
            except Exception as exc:
                logger.error(f"Error al encender foco: {exc}")
                self._reset()
                return False

    def turn_off(self) -> bool:
        """
        Apaga el foco.

        Returns:
            True  — comando enviado correctamente.
            False — servicio deshabilitado o error de red.
        """
        if not self._enabled:
            logger.warning("BulbService: turn_off ignorado (deshabilitado)")
            return False

        with self._lock:
            try:
                bulb = self._get_bulb()
                bulb.turn_off()
                self._state = False
                logger.info("Foco RGB → APAGADO")
                return True
            except Exception as exc:
                logger.error(f"Error al apagar foco: {exc}")
                self._reset()
                return False

    def get_state(self) -> str:
        """
        Consulta el estado real del foco (llamada de red).

        Returns:
            'on' | 'off' | 'unknown'
        """
        if not self._enabled:
            return 'unknown'

        with self._lock:
            try:
                bulb = self._get_bulb()
                data = bulb.status()
                # DP 20 = switch_led (True/False)
                is_on = data.get('dps', {}).get(self._DP_SWITCH, None)
                if is_on is None:
                    return self.current_state
                self._state = bool(is_on)
                return 'on' if self._state else 'off'
            except Exception as exc:
                logger.error(f"Error al consultar estado del foco: {exc}")
                self._reset()
                return self.current_state


###############################################################################
# Singleton — importado por server.py como `tapo_service`
# (nombre mantenido para no cambiar server.py)
###############################################################################

tapo_service = BulbService()
